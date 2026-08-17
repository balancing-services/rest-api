---
name: balancing-services-api
description: Integrate with, query or migrate to the Balancing Services REST API (https://api.balancing.services/v2), which serves European electricity balancing market data — imbalance prices and volumes, balancing energy and capacity volumes, prices and bids, cross-border exchange, day-ahead prices. Use when writing or reviewing client code against this API, picking endpoints and parameters, building pagination or incremental-polling loops, or upgrading an existing v1 client to v2.
---

# Balancing Services REST API

A commercial REST API over European electricity balancing market data: imbalance, balancing
energy, balancing capacity, cross-border exchange and day-ahead prices, harmonised across TSOs
and areas.

- Base URL: `https://api.balancing.services/v2` (v1 remains served at `.../v1`)
- Auth: `Authorization: Bearer <token>` on every request. Request a token from info@balancing.services
- Interactive docs: https://api.balancing.services/v2/documentation
- Canonical schema: `openapi.yaml` at the repository root — shipped with this plugin (two
  directories up from this skill) and published at https://github.com/balancing-services/rest-api.
  Always the final word on paths, parameters, response fields, nullability and enum values: read it
  rather than guessing, and never invent a field name

## Response shape

Every endpoint returns the same envelope. For `/imbalance/prices`:

```json
{
  "queriedPeriod": { "startAt": "2025-01-01T00:00:00Z", "endAt": "2025-01-02T00:00:00Z" },
  "data": [
    { "area": "EE", "eicCode": "10Y1001A1001A39I", "currency": "EUR", "direction": "positive",
      "prices": [
        { "period": { "startAt": "2025-01-01T00:00:00Z", "endAt": "2025-01-01T00:15:00Z" },
          "pricePerMwh": 45.50 }
      ] }
  ],
  "nextCursor": "v1:AAAAAYwBAgMEBQYHCAkKCw==",
  "hasMore": true,
  "nextUpdatedSince": "2025-01-02T09:15:00Z"
}
```

`data` holds groups: the dimensions (area, reserve type, direction, currency, …) are stated once
per group, and the inner array carries one entry per period. The inner array's name, value fields
and exact group dimensions differ per endpoint — read them from the schema, never by analogy with
another endpoint. (The `v1:` seen in the spec's cursor examples is not an API version — cursors
are opaque.)

## Endpoints

All take `period-start-at` and `period-end-at`; the last column lists what else is required.

| Endpoint | Returns | Also required |
|---|---|---|
| `GET /imbalance/prices` | Imbalance prices per MWh, grouped by direction (`positive`/`symmetric`/`negative`) | `area` |
| `GET /imbalance/prices/forecast` | Experimental. Imbalance price forecasts as predictive distributions: `quantiles` gives one level/price pair per quantile level, ascending by level; `degraded` flags a less trustworthy forecast | `area` |
| `GET /imbalance/prices/history` | Experimental. The revision history of `/imbalance/prices`: the sequence of values held for a period, each stamped with its `observedAt` — a lineage, normally ending at the value served now | `area` |
| `GET /imbalance/total-volumes` | Settled total imbalance volume as average power, direction `surplus`/`deficit`/`balanced` per period | `area` |
| `GET /imbalance/total-volumes/current` | Experimental. Provisional open area control error at 1-minute resolution, roughly 25 min behind real time, ~90 days retained | `area` |
| `GET /imbalance/total-volumes/history` | Experimental. The revision history of `/imbalance/total-volumes`: the sequence of values held for a period, each stamped with its `observedAt` — a lineage, normally ending at the value served now | `area` |
| `GET /balancing/energy/activated-volumes` | Activated balancing energy as average power in MW, by direction and activation type | `area`, `reserve-type` |
| `GET /balancing/energy/offered-volumes` | Offered balancing energy volumes | `area`, `reserve-type` |
| `GET /balancing/energy/prices` | Balancing energy prices per MWh | `area`, `reserve-type` |
| `GET /balancing/energy/bids` | Energy bid curves (`volumeInMw`, `pricePerMwh`), grouped by delivery period | `area`, `reserve-type` |
| `GET /balancing/energy/demand` | Experimental. Balancing energy the TSO requested | `area`, `reserve-type` |
| `GET /balancing/energy/satisfied-demand` | Experimental. The part of that demand which was satisfied | `area`, `reserve-type` |
| `GET /balancing/energy/cross-border-marginal-prices` | Experimental. Cross-border purchased marginal prices per MWh | `area`, `reserve-type` |
| `GET /balancing/energy/cross-border-volumes` | Balancing energy exchanged over one border, both directions, split by activation type | `area`, `other-area`, `reserve-type` |
| `GET /balancing/capacity/bids` | Capacity bid curves grouped by delivery period; each bid carries its `procurement` and `status` (`offered`/`accepted`) | `area`, `reserve-type` |
| `GET /balancing/capacity/prices` | Capacity prices per MW per hour, grouped per procurement | `area`, `reserve-type` |
| `GET /balancing/capacity/procured-volumes` | Procured capacity in MW, grouped per procurement | `area`, `reserve-type` |
| `GET /balancing/capacity/demand` | Experimental. Capacity the TSO set out to procure: `totalDemandInMw`, `localDemandInMw`, per procurement, with a `demandBasis` | `area`, `reserve-type` |
| `GET /balancing/capacity/cross-zonal-allocation` | Allocated cross-zonal capacity over one border, both directions | `area`, `other-area`, `reserve-type` |
| `GET /balancing/cross-border/available-capacity` | Capacity available for balancing energy exchange over one border, per direction | `area`, `other-area`, `reserve-type` |
| `GET /energy/day-ahead/prices` | Experimental. Day-ahead wholesale prices per MWh in the zone's native currency | `area` |

Endpoints marked experimental may change or be withdrawn without a deprecation period.
`reserve-type` is one of `FCR`, `aFRR`, `mFRR`, `RR`.

## Request semantics

**Period window.** `period-start-at`/`period-end-at` are UTC ISO-8601 instants and both are
required. Matching is by *overlap*, not containment: a record is returned when its own period
overlaps the requested window, so a query that starts mid-period still returns that period's
record in full. Compare against each record's own `period`, not the query bounds.

**Areas.** `area` takes an area code from the `Area` enum in `openapi.yaml` — bidding zones and
control areas (`EE`, `FI`, `DE`, `SE3`, `IT_NORTH`, …) plus aggregates: `BALTICS` (the Baltic LFC
block that `EE`, `LV` and `LT` balance as one market), `IT` (Italy across its bidding zones) and
`DE` alongside the four German TSO areas. Data exists only where the underlying source publishes
it — an area/dataset combination with no data returns an empty `data` array, not an error. Do not
treat empty as failure.

**Pagination is always on.** Every endpoint accepts `cursor` and `limit` and every response
carries `nextCursor` and `hasMore`. `limit` defaults to 100 (max 1000), except
`/imbalance/total-volumes/current` (default 120, max 1440) and
`/balancing/energy/cross-border-marginal-prices` (default 1000, max 10000). A request without
pagination parameters returns the *first page*, not the whole window — follow `nextCursor` until
`hasMore` is `false`, repeating every other query parameter unchanged on each page. Cursors are
opaque: never parse or construct one.

**Incremental polling.** Pass `updated-since` to get only the records that changed strictly after
that timestamp, within the (still mandatory) period window. Every response carries `nextUpdatedSince`
— feed exactly that value into the next poll over the same window; a timestamp you derive
yourself can silently skip changes. The watermark deliberately lags, so consecutive polls overlap
and a record can arrive more than once: upsert on consume. On the bid endpoints the unit of change
is a stored bid set, not an individual bid: any change re-delivers all of the set's bids, unchanged
ones included, and since bids carry no client-visible identifier there is no key to upsert on —
replace per set, and re-fetch without `updated-since` when exactness matters (see
references/pagination-and-polling.md).

## Gotchas

- **Bids are grouped by period.** `data[].periods[]` states the `period` once and carries that
  period's `bids`. `limit` counts individual bids, so a page can end *inside* a period entry —
  when `hasMore` is true, merge entries on the group's dimensions plus the period rather than
  appending them. Bids within a period entry have no guaranteed order; sort by price yourself if
  you need the merit order.
- **Capacity data nests the procurement.** Capacity prices, procured volumes and demand carry a
  required `procurement` object with `procuredAt` inside it (not a flat field), and each capacity
  bid carries its own `procurement` — so one period entry can mix bids from several procurement
  rounds. `procuredAt` distinguishes yearly from hourly auctions and re-runs; treat it as part of
  the group key.
- **`activationType` has four values.** `direct` and `scheduled` apply to mFRR; `unspecified` is
  mFRR with no direct/scheduled breakdown published; `notApplicable` means the reserve type has no
  activation-type concept at all (FCR, aFRR, RR). Do not collapse `unspecified` into
  `notApplicable` — they answer different questions.
- **Field names carry their units.** `volumeInMw`, `capacityInMw`, `averagePowerInMw`,
  `pricePerMwh`, `pricePerMwPerHour`, `availableCapacityInMw`, `totalDemandInMw`,
  `localDemandInMw`. There are no unit-less aliases on v2.
- **Capacity demand can double-count.** Sum only `additive` demand across procurements of one
  period; `substitutive` restates demand already covered by another procurement.
- **Forecast quantiles are self-describing.** Each forecast on `/imbalance/prices/forecast` states
  the grid it was made on — read `level` off every quantile rather than indexing by a position you
  hardcoded. Levels are decimals strictly between 0 and 1 (0.5 the median).
- **Currency varies by area** (`EUR`, `BGN`, `CHF`, `HUF`, `PLN`, `RON`, `UAH`) and is stated per
  group — never assume euros.

## Quick start

```bash
curl -s "https://api.balancing.services/v2/imbalance/prices?area=EE&period-start-at=2025-01-01T00:00:00Z&period-end-at=2025-01-02T00:00:00Z&limit=1000" \
  -H "Authorization: Bearer $BALANCING_SERVICES_TOKEN"
```

An official Python client is published as `balancing-services` (`pip install balancing-services`).
It exposes one module per operation under `balancing_services.api.default`, and enum-typed
parameters take plain strings (`area="EE"`). See `clients/python/README.md` in this repository.

## References

- Read `references/migrating-from-v1.md` when the user has existing v1 integration code, or
  mentions v1, `/v1` URLs, or fields like `not_applicable`, `volume` or `price` without units.
- Read `references/pagination-and-polling.md` before writing any pagination or polling loop.
- Read `references/error-handling.md` when handling failures, retries or rate limits.
