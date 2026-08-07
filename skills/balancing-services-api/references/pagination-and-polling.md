# Pagination and incremental polling

Read this before writing a loop against the API. Every v2 endpoint is paginated, and the two most
common bugs — silently truncating a window, and skipping a change while polling — both come from
short-cutting the contract below.

## Pagination contract

Request parameters, accepted by every endpoint:

| Parameter | Required | Notes |
|---|---|---|
| `cursor` | no | The `nextCursor` of the previous page. Omit for the first page |
| `limit` | no | Page size. Default 100, max 1000 unless noted below |

Two endpoints have their own bounds, sized to their resolution:

| Endpoint | Default `limit` | Max `limit` |
|---|---|---|
| `/imbalance/total-volumes/current` | 120 | 1440 (one day of per-minute values) |
| `/balancing/energy/cross-border-marginal-prices` | 1000 | 10000 |

Every response carries:

- `hasMore` — `true` while further pages exist.
- `nextCursor` — opaque string to pass as `cursor` on the next request; `null` on the last page.
- `queriedPeriod` — the window you asked for, echoed back.
- `nextUpdatedSince` — the polling watermark (see below). Always present, even when `data` is empty.

Rules that are easy to get wrong:

- **A request without `cursor` and `limit` returns the first page, not the whole window.** There is
  no mode that returns everything in one response.
- **Repeat every other query parameter unchanged on each page.** The cursor carries the position
  only; `area`, `reserve-type`, the period bounds and `updated-since` must be resent identically.
- **Cursors are opaque.** Never parse, construct, truncate or reuse one across endpoints. If a
  cursor is rejected, recover by restarting the drain with no cursor.
- **Drive the loop off `hasMore`, not off `len(data)`.** A page can be shorter than `limit` and
  still have successors, and `data` counts *groups*, not records.

### Merging grouped responses across pages

`data` holds groups (area, reserve type, direction, currency, …) with the periods nested inside, and
that grouping is applied *per page*. A group whose records straddle a page boundary can appear on
both pages. Accumulate by merging on the group's dimensions — appending groups blindly can yield two
entries for the same series.

For the bid endpoints (`/balancing/energy/bids`, `/balancing/capacity/bids`) there is one more
level: `limit` counts **individual bids**, not groups or period entries, so a page can end in the
middle of a delivery period. When `hasMore` is `true`, treat the last period entry as incomplete and
merge on the group's dimensions **plus** the period. Bids inside an entry have no guaranteed order —
sort by price yourself for the merit order.

`/balancing/capacity/cross-zonal-allocation` groups by border, reserve type and period duration, so
one border can appear as several groups in one drain when its allocations differ in length.

### Draining a window

```python
def drain(session, url, params, limit=1000):
    cursor = None
    while True:
        response = session.get(url, params={**params, "limit": limit,
                                            **({"cursor": cursor} if cursor else {})})
        # Error handling elided: retry 429 per Retry-After and 5xx with backoff, surface
        # the Problem body otherwise — see error-handling.md. Retry a failed page with the
        # same cursor rather than restarting the drain.
        page = response.json()
        yield page
        if not page["hasMore"]:
            return
        cursor = page["nextCursor"]
```

Page size is a throughput/latency trade-off: 10–50 for interactive UIs, 100–500 as a default,
500–1000 for batch loads. To resume after a crash mid-drain, checkpoint the last `nextCursor`
alongside the data you have written.

## Incremental polling with `updated-since`

`updated-since` narrows a query to the records whose stored value changed strictly after the given
timestamp, *in addition to* the mandatory period window. It is not a global change feed: the window
still bounds the query, so polling means "re-ask for this window, but only the changes". On the bid
endpoints change is tracked per bid set rather than per record — see below.

Records carry no per-record change timestamp. Instead, every response reports `nextUpdatedSince` —
the watermark to feed into the next poll. It comes from the server, so your clock never enters the
loop.

Contract:

- Every page of one drain reports the **same** `nextUpdatedSince`. Read it once (any page will do)
  and store it after the drain completes.
- **Pass back exactly that value** on the next poll over the same window. A timestamp you derive
  yourself — for instance the newest period you saw, or "now" — sits ahead of the point the drain is
  actually complete to, and can silently skip changes.
- The watermark deliberately lags real time, so consecutive polls overlap slightly and a record can
  be delivered more than once. **Delivery is at-least-once: upsert on consume.** Duplicates are the
  designed-for cost; a lost change is not tolerated, which is why the lag exists.
- On the bid endpoints the unit of change is a **bid set** — the bids stored and tracked together
  for one delivery period — not an individual bid: any change to a set (a new bid, a revised one, a
  withdrawal) re-delivers all of the set's bids, including the ones that did not change themselves.
  A period entry in a response is not always a single set — capacity bids procured in separate
  rounds are separate sets, as are distinctions the response's grouping does not surface — so a
  re-delivered set does not imply the period entry around it is complete. And since bids carry no
  client-visible identifier, there is no key to upsert on: a filtered poll tells you a set changed
  and hands you its current bids, but not which bid was added, revised, or withdrawn — it cannot
  maintain an exact bid-level mirror on its own. When exactness matters, reconcile with an
  unfiltered re-fetch (see below).
- Do not mix cursors between polls; each poll is its own drain, restarted from your stored
  watermark.

### Recipe

1. Drain the window with no `updated-since`, following `nextCursor` until `hasMore` is `false`. Keep
   the response's `nextUpdatedSince`.
2. On the next poll, pass that value as `updated-since` and drain all pages again. An empty `data`
   array means nothing changed.
3. Replace the stored watermark with the new `nextUpdatedSince` and repeat.

Persist the watermark wherever you persist the data, ideally in the same transaction. On restart,
resuming from the last stored watermark re-delivers a little and loses nothing.

```python
def poll(session, url, params, store, watermark=None):
    """One poll cycle. Returns the watermark to use next time."""
    poll_params = dict(params)
    if watermark:
        poll_params["updated-since"] = watermark

    next_watermark = watermark
    for page in drain(session, url, poll_params):
        for group in page["data"]:
            store.upsert(group)          # idempotent: records may repeat across polls; bids: replace per set
        next_watermark = page["nextUpdatedSince"]   # same value on every page of one drain

    store.save_watermark(next_watermark)  # same transaction as the upserts, ideally
    return next_watermark
```

When merging a filtered response into stored data, merge records by period rather than by group
identity — a filtered response carries only what changed (for bids, only the changed sets, each
delivered whole), so its groups need not line up one-to-one with the groups of a full drain.

### Withdrawals and the unfiltered re-fetch

A poller only sees rows that exist. Bids are the one dataset where deletion is normal operation: a
bid withdrawn at the source is deleted here without replacement, and no response ever names it.

The withdrawal does move its bid set's change time, so the set's *surviving* bids are re-delivered.
That narrows the blind spot but does not close it: a set whose bids were all withdrawn has no
survivors to re-deliver, a period entry can span several independently-tracked sets, and a set that
changes mid-drain defers its remaining bids to the next poll — so a filtered poll is not guaranteed
to carry a period's complete bid set. If bid-level accuracy matters, periodically re-fetch the full
window without `updated-since` and reconcile.
