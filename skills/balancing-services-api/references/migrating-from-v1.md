# Migrating a client from v1 to v2

Version 1 remains served at `https://api.balancing.services/v1` and is unaffected by everything
below, so the migration can be done at your own pace and rolled back by pointing the base URL
back at `/v1`.

## What changed, and why an unchanged client breaks

v2 is the first major-version bump, and it spends that budget on four things: pagination everywhere,
incremental polling, a response shape that states each dimension once instead of repeating it, and
the removal of ambiguous names left over from 1.x.

A v1 client repointed at `/v2` without changes typically fails in this order:

1. **It silently truncates.** Endpoints that used to return the whole window now return the first
   100 records. No error, no warning — just missing data, which is the failure mode most likely to
   reach production unnoticed. Fix pagination first.
2. **It cannot find its fields.** `volume`, `price`, `capacity` and `averagePowerMW` are gone; bids
   moved a level deeper; `procuredAt` moved inside a `procurement` object.
3. **It rejects enum values.** `activationType` no longer serves `not_applicable`, and serves a new
   `unspecified`; `Problem.type` is no longer a closed set.
4. **Two border endpoints reject the request outright** — 400, missing required `other-area`.

Migrating in the order below keeps each step independently testable.

## 1. Base path

```
- https://api.balancing.services/v1/imbalance/prices?area=EE&...
+ https://api.balancing.services/v2/imbalance/prices?area=EE&...
```

Paths, the `Authorization: Bearer` scheme, area codes, reserve types and the
`period-start-at`/`period-end-at` overlap semantics are unchanged. Interactive docs move to
`https://api.balancing.services/v2/documentation`.

## 2. Pagination is always on

On v1, pagination was piecemeal: endpoints added later in the 1.x line already paginated, while
the original endpoints — imbalance prices and total volumes, activated volumes, energy and
capacity prices, procured volumes, cross-zonal allocation — returned the complete window in one
response (cross-border volumes sat in between, with an opt-in mode: see §10). On v2 every
endpoint accepts `cursor` and `limit`, every response carries
`nextCursor` and `hasMore`, and `limit` defaults to 100 (max 1000). Two endpoints keep wider
bounds: `/imbalance/total-volumes/current` (default 120, max 1440) and
`/balancing/energy/cross-border-marginal-prices` (default 1000, max 10000).

Any code shaped like this is now wrong:

```python
# v1: one request, whole window
response = get(url, params=params).json()
for group in response["data"]:
    ...
```

```python
# v2: drain the pages
cursor = None
while True:
    page = get(url, params={**params, "limit": 1000, **({"cursor": cursor} if cursor else {})}).json()
    for group in page["data"]:
        ...
    if not page["hasMore"]:
        break
    cursor = page["nextCursor"]
```

Repeat every other query parameter unchanged on each page — the cursor carries the position, not
the filters. See `pagination-and-polling.md` before writing the loop for real; the merge rules for
grouped responses matter.

Responses also gained a required `nextUpdatedSince` field, the watermark for the new optional
`updated-since` parameter. Nothing needs to consume it to migrate, but note the reverse direction:
a *v2* client pointed at `/v1` fails, because v1 responses have no `nextUpdatedSince`.

## 3. Bids are grouped by delivery period

Both bid endpoints (`/balancing/energy/bids`, `/balancing/capacity/bids`) previously carried a flat
`bids` array in which every bid repeated its own `period`. v2 states the period once:

```json
// v1
{ "area": "EE", "eicCode": "10Y1001A1001A39I", "reserveType": "mFRR", "direction": "up", "currency": "EUR", "standardProduct": true,
  "bids": [
    { "period": { "startAt": "2025-01-01T00:00:00Z", "endAt": "2025-01-01T01:00:00Z" }, "volumeInMw": 100, "pricePerMwh": 55.25 },
    { "period": { "startAt": "2025-01-01T00:00:00Z", "endAt": "2025-01-01T01:00:00Z" }, "volumeInMw": 40,  "pricePerMwh": 61.00 }
  ] }
```

```json
// v2
{ "area": "EE", "eicCode": "10Y1001A1001A39I", "reserveType": "mFRR", "direction": "up", "currency": "EUR", "standardProduct": true,
  "periods": [
    { "period": { "startAt": "2025-01-01T00:00:00Z", "endAt": "2025-01-01T01:00:00Z" },
      "bids": [
        { "volumeInMw": 100, "pricePerMwh": 55.25 },
        { "volumeInMw": 40,  "pricePerMwh": 61.00 }
      ] }
  ] }
```

Period entries ascend by period start within a group. Bids inside an entry carry no guaranteed
order — sort by price if you need the merit order.

`limit` still counts individual bids, so a page can end in the middle of a period entry. When
`hasMore` is `true`, accumulate by merging on the group's dimensions plus the period; appending
period entries blindly produces two entries for the same period with the bid curve split between
them.

## 4. `procuredAt` moved into a `procurement` object

Affects `/balancing/capacity/prices`, `/balancing/capacity/procured-volumes` and
`/balancing/capacity/demand`. On prices and procured volumes `procuredAt` was also experimental and
nullable in v1; in v2 `procurement` is required and stable, so null-handling branches can go.

```json
// v1
{ "area": "FI", "eicCode": "10YFI-1--------U", "reserveType": "aFRR", "direction": "up", "currency": "EUR",
  "procuredAt": "2024-08-15T14:30:00Z",
  "prices": [ ... ] }
```

```json
// v2
{ "area": "FI", "eicCode": "10YFI-1--------U", "reserveType": "aFRR", "direction": "up", "currency": "EUR",
  "procurement": { "procuredAt": "2024-08-15T14:30:00Z" },
  "prices": [ ... ] }
```

Capacity bids gained the same object, one level deeper — each bid states the procurement it was
submitted to, so a single period entry can mix bids from several procurement rounds:

```json
// v2 /balancing/capacity/bids
{ "period": { "startAt": "...", "endAt": "..." },
  "bids": [
    { "capacityInMw": 50, "pricePerMwPerHour": 12.50, "status": "accepted",
      "procurement": { "procuredAt": "2024-08-15T14:30:00Z" } }
  ] }
```

If your storage keys capacity rows on `(area, reserveType, direction, period)`, add the procurement
to the key.

## 5. `other-area` is now required on two border endpoints

`/balancing/energy/cross-border-volumes` and `/balancing/capacity/cross-zonal-allocation`
previously took `area` alone and returned data across *all* borders of that area. v2 requires both
ends:

```
- GET /v1/balancing/energy/cross-border-volumes?area=FI&reserve-type=mFRR&period-start-at=...
+ GET /v2/balancing/energy/cross-border-volumes?area=FI&other-area=EE&reserve-type=mFRR&period-start-at=...
```

Results still cover both directions of that border (area → other-area and other-area → area), and
each record names them in `fromArea`/`toArea`. A request where `area` equals `other-area` is
rejected with 400.

If your client relied on the all-borders behaviour, enumerate the borders you care about and issue
one request per border. `/balancing/cross-border/available-capacity` already required `other-area`
on v1 and is unchanged.

## 6. Cross-zonal allocation is no longer expanded onto a sub-period grid

`/balancing/capacity/cross-zonal-allocation` returns the allocation records as published, grouped
by border, reserve type and period duration. v1 expanded them onto a common sub-period grid,
splitting one allocation into several equal-valued entries.

Consequences: one border can now yield several groups within one query when its allocations differ
in period duration. Periods within a group all share that group's duration, but durations differ
across groups, and none are sub-divided onto a common grid any more. Read each record's own
`period` and normalise client-side if your model needs a fixed grid.

## 7. `activationType` renames, and gains `unspecified`

| v1 value | v2 value |
|---|---|
| `direct` | `direct` |
| `scheduled` | `scheduled` |
| `not_applicable` (FCR, aFRR, RR) | `notApplicable` |
| `not_applicable` (mFRR with no direct/scheduled breakdown) | `unspecified` |

Two changes at once. The rename to camelCase removes the API's only snake_case enum value. The
split is the substantive one: `notApplicable` now means only "this reserve type has no
activation-type concept", while mFRR records whose source publishes no direct/scheduled breakdown
report `unspecified`. Code that treated `not_applicable` as "not mFRR" will misclassify those mFRR
records unless it handles `unspecified` separately.

Since only mFRR distinguishes activation types, the split settles per query: a call filtered to
`reserve-type=mFRR` can only return `direct`, `scheduled` or `unspecified`, and a call for FCR,
aFRR or RR only `notApplicable`. A v1 call site that filtered on `not_applicable` therefore maps
to exactly one of the new values — which one depends only on the reserve type it queries.

Affects `/balancing/energy/prices`, `/balancing/energy/activated-volumes`,
`/balancing/energy/offered-volumes`, `/balancing/energy/demand`,
`/balancing/energy/satisfied-demand` and `/balancing/energy/cross-border-volumes`. Clients that
parse the enum strictly must accept both new values.

## 8. `Problem.type` is an open string

The error body's `type` was a closed enum in v1 and is a plain string in v2. Generated clients that
exposed it as an enum type now expose a string, so `problem.type.value` and enum-member comparisons
need rewriting.

The wire values are otherwise unchanged: `missing-parameter`, `invalid-parameter`, `unauthorized`,
`forbidden`, `not-found`, `rate-limited`, `not-implemented`, `internal-error`. This also fixes an
omission — v1's enum lacked `not-found`, which 404 responses already returned, so strict clients
could fail to parse a well-formed 404.

Match the values you handle and fall back on `status` for anything else; new types may appear
without a major-version bump. See `error-handling.md`.

## 9. Unit-less fields removed

Deprecated in 1.14.0, removed in 2.0.0. Every explicit-unit name below already exists on v1, so
this step can be done *before* switching base URLs and verified against v1.

| Where | v1 field (removed) | v2 field |
|---|---|---|
| Imbalance prices — `data[].prices[]` | `price` | `pricePerMwh` |
| Imbalance total volumes (incl. `/current`) — `data[].volumes[]` | `averagePowerMW` | `averagePowerInMw` |
| Balancing energy volumes (activated, offered, demand, satisfied demand, cross-border) — `data[].volumes[]` | `volume` | `volumeInMw` |
| Balancing energy prices — `data[].prices[]` | `price` | `pricePerMwh` |
| Energy bids | `volume`, `price` | `volumeInMw`, `pricePerMwh` |
| Capacity bids | `capacity`, `price` | `capacityInMw`, `pricePerMwPerHour` |
| Capacity prices — `data[].prices[]` | `price` | `pricePerMwPerHour` |
| Capacity procured volumes, cross-zonal allocation — `data[].volumes[]` | `volume` | `volumeInMw` |
| Day-ahead prices — `data[].prices[]` | `price` | `pricePerMwh` |
| Cross-border marginal prices — `data[].prices[]` | `price` | `pricePerMwh` |

Capacity demand (`totalDemandInMw`, `localDemandInMw`) and cross-border available capacity
(`availableCapacityInMw`) never had unit-less names.

## 10. Non-paginated mode and the 32-day cap are gone

`/balancing/energy/cross-border-volumes` had an opt-in pagination mode: omitting both `cursor` and
`limit` returned the full result set in one response, bounded to a 32-day period. That mode is
removed, as announced when it was deprecated in 1.x. Pagination is now always on — and, with it,
the 32-day cap is gone, so arbitrarily long windows can be drained page by page.

## 11. Python client: `Enum` → `Literal`

The official `balancing-services` client generates `Literal[...]` string types instead of `Enum`
classes for `Area`, `ReserveType`, `ActivationType`, `Currency`, `Direction`, `EicCode`,
`BidStatus`, `ImbalanceDirection`, `TotalImbalanceDirection` and `DemandBasis`.

```python
# before
from balancing_services.models import Area, ReserveType
response = get_balancing_energy_prices.sync_detailed(
    client=client, area=Area.EE, reserve_type=ReserveType.MFRR, ...
)
print(response.parsed.data[0].area.value)
```

```python
# after
response = get_balancing_energy_prices.sync_detailed(
    client=client, area="EE", reserve_type="mFRR", ...
)
print(response.parsed.data[0].area)
```

Enum-member access (`Area.EE`, `EicCode.VALUE_19`) and the `.value` accessor on those model fields
are gone. The upside is stability: a `Literal` has no positional member names, so adding or
reordering values in the spec can no longer silently rebind `EicCode.VALUE_19` to a different code
between releases.

## Migration checklist

Walk this against the customer's codebase, in order.

- [ ] **Base URL.** Grep for `api.balancing.services/v1`, `/v1/`, and any hardcoded path built from
      a version constant. Confirm there is exactly one place the version is set.
- [ ] **Pagination.** For every call site, confirm the response is drained: `hasMore` is checked and
      `nextCursor` is passed back, with all other parameters repeated. Flag any call that reads
      `data` once and moves on — including ones that "worked" on v1 because the endpoint was
      unpaginated. Watch for pipelines that assume a whole window in one payload (dataframe loads,
      bulk upserts, "row count equals expected periods" assertions).
- [ ] **`other-area`.** Every call to `/balancing/energy/cross-border-volumes` and
      `/balancing/capacity/cross-zonal-allocation` must pass it. Where the old all-borders
      behaviour was used, replace with an explicit list of borders.
- [ ] **Bid parsing.** Grep for `["bids"]`, `.bids` and any model with `bids` at group level.
      Rewrite as `periods[].bids[]`, take the period from the entry, and merge cross-page entries on
      group dimensions plus period.
- [ ] **Field names.** Grep for `"volume"`, `"price"`, `"capacity"`, `"averagePowerMW"` as exact
      keys or attribute names and apply the mapping table. Beware ORM columns, chart series names
      and CSV headers that happen to share the names.
- [ ] **`procuredAt`.** Grep for it; rewrite to `procurement.procuredAt`, add it to capacity bid
      parsing, and drop null-handling on capacity prices and procured volumes. Extend any storage
      key that identifies a capacity row without the procurement.
- [ ] **`activationType`.** Grep for `not_applicable`. Decide, per site, whether it meant "no
      activation-type concept" (`notApplicable`) or "any mFRR without a breakdown"
      (`unspecified` too). Make the parse non-strict or add both values.
- [ ] **Cross-zonal allocation.** If the client assumed uniform period lengths or one group per
      border, handle mixed durations and multiple groups.
- [ ] **Error handling.** Replace enum comparisons on `Problem.type` with string comparison plus a
      `status` fallback; make sure an unknown `type` does not raise.
- [ ] **Python client.** Upgrade `balancing-services`, replace `Area.EE`-style members with plain
      strings, and remove `.value` on enum-typed model fields.
- [ ] **Optional: incremental polling.** If the client re-downloads a fixed window on a schedule,
      switch it to `updated-since` with the `nextUpdatedSince` watermark. See
      `pagination-and-polling.md`.
- [ ] **Verify.** Re-run one representative query per endpoint against `/v1` and `/v2` over the same
      window and reconcile record counts and values. Truncated pagination is the failure this
      catches.
