# Changelog

All notable changes to the Balancing Services REST API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- The official Python client's generated enum validators (`check_area`, `check_currency`, and the other `check_*` helpers) now type-check under mypy 1.x. The `literal_enums` output returned a bare `str` where a `Literal[...]` was expected, which only mypy 2.x accepts by narrowing the membership test; the validators now wrap the return in `cast(...)`, so `mypy` passes on every supported version. This is purely a static-typing fix — `cast` is a no-op at runtime, so there is no API, wire, or runtime-behaviour change

## [2.0.0] - 2026-07-25

### Added
- Incremental polling on every data endpoint: an optional `updated-since` query parameter filters to records changed strictly after the given timestamp, and every paginated response carries a `nextUpdatedSince` watermark to pass back on the next poll over the same window. Every page of one drain reports the same watermark; it deliberately lags real time so consecutive polls overlap slightly — a record may be delivered more than once, so upsert on consume

### Changed
- The API is served under a new base path: `https://api.balancing.services/v2`. Version 1 remains available at `https://api.balancing.services/v1`
- **Breaking:** Every data endpoint is now paginated. All endpoints accept `cursor` and `limit`, and every response carries `nextCursor` and `hasMore`. `limit` defaults to 100 (max 1000) when omitted, so a request without pagination parameters returns the first page rather than the whole result set — follow `nextCursor` until `hasMore` is `false` to retrieve everything. Two endpoints keep their own bounds: `/imbalance/total-volumes/current` (default 120, max 1440) and `/balancing/energy/cross-border-marginal-prices` (default 1000, max 10000)
- **Breaking:** The allocated cross-zonal capacity endpoint (`/balancing/capacity/cross-zonal-allocation`) returns the underlying allocation records as published, grouped by border, reserve type and period duration. Previously allocations were expanded onto a common sub-period grid, splitting one allocation into several equal-valued entries; a border can now yield several groups within one query when the allocations differ in period duration
- **Breaking:** The cross-border balancing energy volumes (`/balancing/energy/cross-border-volumes`) and allocated cross-zonal capacity (`/balancing/capacity/cross-zonal-allocation`) endpoints require a new `other-area` query parameter, so both ends of the border must be given. Results cover both directions (area → other-area and other-area → area), and a request where `area` equals `other-area` is rejected with a 400. Previously `area` alone selected data over all borders of that area
- The cross-border endpoints — cross-border balancing energy volumes (`/balancing/energy/cross-border-volumes`), allocated cross-zonal capacity (`/balancing/capacity/cross-zonal-allocation`) and cross-border available capacity (`/balancing/cross-border/available-capacity`) — are no longer experimental and are now considered stable
- **Breaking:** The balancing energy bids (`/balancing/energy/bids`) and balancing capacity bids (`/balancing/capacity/bids`) endpoints group bids by delivery period. Each bid group carries a `periods` array whose entries state the `period` once and hold that period's `bids`, replacing the flat `bids` array where every bid repeated its own `period` field. Period entries ascend by period start within their group; bids within a period entry carry no guaranteed order — sort by price client-side for the merit order. `limit` still counts individual bids, so a page can end inside a period entry — when `hasMore` is `true`, merge entries on the group's dimensions plus the period when accumulating pages
- **Breaking:** The balancing capacity prices (`/balancing/capacity/prices`), procured volumes (`/balancing/capacity/procured-volumes`) and demand (`/balancing/capacity/demand`) endpoints nest `procuredAt` inside a `procurement` object instead of carrying it as a flat field on the group. `procurement` is required and no longer experimental — on prices and procured volumes `procuredAt` was previously experimental and nullable. Capacity bids (`/balancing/capacity/bids`) now also carry `procurement`: each bid states the procurement it was submitted to, so a single period entry can mix bids from multiple procurement rounds
- **Breaking:** The `activationType` enum gains a fourth value, `unspecified`, marking mFRR records with no direct/scheduled breakdown — the source does not publish one, or the product does not define one. Such records previously reported `not_applicable`, which is now reserved for reserve types that have no activation-type concept at all (FCR, aFRR, RR), so mFRR records that used to come back as `not_applicable` now come back as `unspecified`. Affects every endpoint carrying `activationType`: balancing energy prices (`/balancing/energy/prices`), activated volumes (`/balancing/energy/activated-volumes`), offered volumes (`/balancing/energy/offered-volumes`), demand (`/balancing/energy/demand`), satisfied demand (`/balancing/energy/satisfied-demand`) and cross-border volumes (`/balancing/energy/cross-border-volumes`). Clients that parse the enum strictly must accept the new value
- **Breaking:** The `type` field of the `Problem` error body is an open string instead of a closed enum, so generated clients that exposed it as an enum now expose a plain string. New problem types may be introduced without a major-version bump — match the values you handle and fall back on `status` for anything you do not recognise. This also corrects the omission of `not-found`, which 404 responses already returned but the enum rejected. The wire values are otherwise unchanged: `missing-parameter`, `invalid-parameter`, `unauthorized`, `forbidden`, `not-found`, `rate-limited`, `not-implemented`, `internal-error`
- **Breaking:** The `activationType` value `not_applicable` is renamed to camelCase `notApplicable`, aligning it with the spec's camelCase convention — it was the only snake_case enum value in the API. This is the value served for reserve types that have no activation-type concept at all (FCR, aFRR, RR); the `unspecified` value for mFRR is unaffected. Clients that parse the enum strictly must accept `notApplicable` in place of `not_applicable` on every endpoint carrying `activationType`. Version 1 is unaffected and continues to serve `not_applicable`
- **Breaking:** The official Python client now generates `Literal[...]` string types instead of `Enum` classes for every enum — `Area`, `ReserveType`, `ActivationType`, `Currency`, `Direction`, `EicCode`, `BidStatus` and the imbalance/demand enums (`ImbalanceDirection`, `TotalImbalanceDirection`, `DemandBasis`). Consumers pass and compare bare string values (`area="EE"` instead of `area=Area.EE`); enum-member access such as `Area.EE` or `EicCode.VALUE_19`, and the `.value` accessor on those model fields, is removed. The upside: because a `Literal` has no positional member names, adding or reordering enum values in the spec can no longer silently rebind one (e.g. `EicCode.VALUE_19` pointing at a different code across releases)

### Removed
- **Breaking:** The opt-in pagination mode on the cross-border energy volumes endpoint (`/balancing/energy/cross-border-volumes`), where omitting both `cursor` and `limit` returned the full result set in a single response, bounded to a 32-day period. Pagination is now always on and the 32-day period cap is gone, as announced when the mode was deprecated in 1.x
- **Breaking:** The ambiguous unit-less fields `volume`, `averagePowerMW`, `capacity`, and `price` are removed across every response schema in favour of their explicit-unit counterparts (`volumeInMw`, `averagePowerInMw`, `capacityInMw`, `pricePerMwh`, `pricePerMwPerHour`), as announced when they were deprecated in 1.14.0

## [1.20.0] - 2026-07-22

### Added
- Support for the `UA` area (Ukraine IPS); the corresponding EIC code `10Y1001C--000182` is added to the `EicCode` enum; `UAH` is added to the `Currency` enum since UA prices are denominated in hryvnia

## [1.19.0] - 2026-07-12

### Added
- Support for the `BALTICS` area, the Baltic LFC block that Estonia (`EE`), Latvia (`LV`) and Lithuania (`LT`) balance as one market; the corresponding EIC code `10Y1001A1001A94A` is added to the `EicCode` enum

## [1.18.0] - 2026-07-09

### Added
- Experimental endpoint for balancing capacity demand (`/balancing/capacity/demand`): the balancing capacity the TSO set out to procure, grouped per procurement so it can be compared against procured volumes. Each demand splits into the total requirement (`totalDemandInMw`) and the in-area floor (`localDemandInMw`), and each procurement group carries a `demandBasis` (`additive`/`substitutive`) telling whether it adds to the delivery period's total requirement or restates demand of an earlier procurement

### Fixed
- Corrected the cross-border available capacity endpoint (`/balancing/cross-border/available-capacity`) description: the value is no longer described as net of scheduled flows
- Updated the cross-border available capacity endpoint's parameter examples to a border and reserve type the API actually serves (`mFRR` on `ES`–`PT` instead of `aFRR` on `FI`–`SE3`)

## [1.17.0] - 2026-07-07

### Added
- Experimental endpoint for current (provisional) total imbalance volumes (`/imbalance/total-volumes/current`): the open area control error at 1-minute resolution, published near real time and superseded by the settled volumes on `/imbalance/total-volumes`

## [1.16.0] - 2026-06-16

### Added
- Experimental endpoint for cross-border available capacity (`/balancing/cross-border/available-capacity`)

## [1.15.0] - 2026-06-10

### Added
- Experimental endpoints for balancing energy demand (`/balancing/energy/demand`) and satisfied balancing energy demand (`/balancing/energy/satisfied-demand`)

### Changed
- The offered balancing energy volumes endpoint (`/balancing/energy/offered-volumes`) is no longer experimental and is now considered stable

## [1.14.0] - 2026-06-03

### Added
- Explicit-unit field names across response schemas, so the unit is unambiguous from the field name alone: `volumeInMw` (alongside `volume` in `BalancingEnergyVolume`, `BalancingCapacityVolume`, and energy bids), `averagePowerInMw` (alongside `averagePowerMW` in total imbalance volumes), `capacityInMw` (alongside `capacity` in capacity bids), `pricePerMwh` (alongside `price` in imbalance, balancing energy, day-ahead, cross-border marginal prices, and energy bids), and `pricePerMwPerHour` (alongside `price` in capacity prices and capacity bids). Each new field carries the same value as the field it replaces

### Deprecated
- The ambiguous unit-less fields `volume`, `averagePowerMW`, `capacity`, and `price` are deprecated in favour of their explicit-unit counterparts (`volumeInMw`, `averagePowerInMw`, `capacityInMw`, `pricePerMwh`, `pricePerMwPerHour`). They remain populated in v1 and will be removed in the next major version

## [1.13.0] - 2026-05-29

### Added
- Support for the aggregate `IT` (Italy) area, returning data aggregated across the Italian bidding zones (`IT_NORTH`, `IT_CENTER_NORTH`, `IT_CENTER_SOUTH`, `IT_SOUTH`, `IT_CALABRIA`, `IT_SICILY`, `IT_SARDINIA`); the corresponding EIC code `10YIT-GRTN-----B` is added to the `EicCode` enum

## [1.12.0] - 2026-05-21

### Added
- Cursor-based pagination for the cross-border balancing energy volumes endpoint (`/balancing/energy/cross-border-volumes`) via optional `cursor` and `limit` query parameters

### Deprecated
- The non-paginated mode of the cross-border balancing energy volumes endpoint (`/balancing/energy/cross-border-volumes`) — omitting both `cursor` and `limit` to receive the full result set in one response — is deprecated. In the next major version `limit` will take a default value when omitted, so requests will always be paginated rather than returning the full result set in a single response

## [1.11.0] - 2026-05-13

### Added
- Experimental endpoint for day-ahead energy prices (`/energy/day-ahead/prices`)

## [1.10.0] - 2026-04-30

### Changed
- Cross-border balancing energy volumes endpoint (`/balancing/energy/cross-border-volumes`) now splits results by activation type — for mFRR, `direct` and `scheduled` activations are returned as separate entries; non-mFRR reserve types use `not_applicable`

## [1.9.0] - 2026-04-28

### Added
- Experimental endpoint for cross-border balancing energy volumes (`/balancing/energy/cross-border-volumes`)

## [1.8.0] - 2026-03-23

### Added
- Experimental endpoint for cross-border purchased marginal prices (`/balancing/energy/cross-border-marginal-prices`)

## [1.7.1] - 2026-03-16

### Added
- CLI: handle rate limiting (HTTP 429) with automatic retries using the Retry-After header
- Document `Retry-After` and `X-RateLimit-Limit` response headers on 429 responses in OpenAPI spec

## [1.7.0] - 2026-03-02

### Added
- Support for CHF (Swiss Franc) currency
- Document price units (currency/MWh, currency/MW per hour) in endpoint descriptions

## [1.6.0] - 2026-01-30

### Added
- Experimental endpoint for offered balancing energy volumes (`/balancing/energy/offered-volumes`)
- Experimental endpoint for cross-zonal capacity allocation (`/balancing/capacity/cross-zonal-allocation`)

## [1.5.1] - 2025-11-09

### Fixed
- Python client crash when `procuredAt` field is `null` in `BalancingCapacityPrices` and `BalancingCapacityVolumes` responses (#8)

## [1.5.0] - 2025-11-07

### Added
- Support for Germany (DE) as a unified area in addition to existing German TSO areas

## [1.4.1] - 2025-10-25

### Changed
- Reorder `procuredAt` field to appear before `prices` and `volumes` arrays in `BalancingCapacityPrices` and `BalancingCapacityVolumes` schemas

## [1.4.0] - 2025-10-25

### Added
- Support for Python 3.13 in the Python client library

## [1.3.0] - 2025-10-25

### Changed
- Move `procuredAt` field from individual price/volume items to `BalancingCapacityPrices` and `BalancingCapacityVolumes` containers

## [1.2.0] - 2025-10-25

### Added
- Support for `symmetric` direction in balancing services to enable FCR (Frequency Containment Reserve) products
- Support for additional currencies: HUF (Hungarian Forint), PLN (Polish Zloty), and RON (Romanian Leu)
- Version bumping script (`scripts/bump-version.sh`) to automate version updates across repository files
- Automated Python client publishing workflow

## [1.1.1] - 2025-10-24

### Fixed
- Python client documentation examples now use correct types (`Area` enum and `datetime` objects) instead of strings (#1318)

### Added
- Automated tests for README code examples to prevent documentation drift

## [1.1.0] - 2025-10-22

### Added
- Official Python client library generated from OpenAPI specification
- `procuredAt` timestamp field to `BalancingCapacityPrice` and `BalancingCapacityVolume` schemas (#1)
  - Enables distinguishing between multiple procurement rounds (e.g., D-2 vs D-1 auctions)
  - Marked as EXPERIMENTAL - may change without standard deprecation period
  - Optional field, initially rolled out for markets with multiple auctions

### Changed
- Simplified Python client README by removing endpoint listing to avoid documentation drift

## [1.0.0] - 2025-10-20

### Added
- Initial public release of Balancing Services REST API specification
- Imbalance prices endpoint (`/imbalance/prices`)
- Imbalance total volumes endpoint (`/imbalance/total-volumes`)
- Balancing energy activated volumes endpoint (`/balancing/energy/activated-volumes`)
- Balancing energy prices endpoint (`/balancing/energy/prices`)
- Balancing energy bids endpoint (`/balancing/energy/bids`)
- Balancing capacity bids endpoint (`/balancing/capacity/bids`)
- Balancing capacity prices endpoint (`/balancing/capacity/prices`)
- Balancing capacity procured volumes endpoint (`/balancing/capacity/procured-volumes`)
- Support for 40+ European areas (AT, BE, BG, CH, CZ, DE, DK, EE, ES, FI, FR, GR, HR, HU, IT, LT, LV, NL, NO, PL, PT, RO, RS, SE, SI, SK)
- Cursor-based pagination for large result sets (bids endpoints)
- Bearer token authentication
- RFC 7807 Problem Details error handling
- Support for multiple reserve types (FCR, aFRR, mFRR, RR)
- UTC timestamp-based period filtering
- OpenAPI 3.0.3 specification

[Unreleased - 2.0.0]: https://github.com/balancing-services/rest-api/compare/v1.20.0...HEAD
[1.20.0]: https://github.com/balancing-services/rest-api/compare/v1.19.0...v1.20.0
[1.19.0]: https://github.com/balancing-services/rest-api/compare/v1.18.0...v1.19.0
[1.18.0]: https://github.com/balancing-services/rest-api/compare/v1.17.0...v1.18.0
[1.17.0]: https://github.com/balancing-services/rest-api/compare/v1.16.0...v1.17.0
[1.16.0]: https://github.com/balancing-services/rest-api/compare/v1.15.0...v1.16.0
[1.15.0]: https://github.com/balancing-services/rest-api/compare/v1.14.0...v1.15.0
[1.14.0]: https://github.com/balancing-services/rest-api/compare/v1.13.0...v1.14.0
[1.13.0]: https://github.com/balancing-services/rest-api/compare/v1.12.0...v1.13.0
[1.12.0]: https://github.com/balancing-services/rest-api/compare/v1.11.0...v1.12.0
[1.11.0]: https://github.com/balancing-services/rest-api/compare/v1.10.0...v1.11.0
[1.10.0]: https://github.com/balancing-services/rest-api/compare/v1.9.0...v1.10.0
[1.9.0]: https://github.com/balancing-services/rest-api/compare/v1.8.0...v1.9.0
[1.7.1]: https://github.com/balancing-services/rest-api/compare/v1.7.0...v1.7.1
[1.7.0]: https://github.com/balancing-services/rest-api/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/balancing-services/rest-api/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/balancing-services/rest-api/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/balancing-services/rest-api/compare/v1.4.1...v1.5.0
[1.4.1]: https://github.com/balancing-services/rest-api/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/balancing-services/rest-api/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/balancing-services/rest-api/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/balancing-services/rest-api/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/balancing-services/rest-api/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/balancing-services/rest-api/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/balancing-services/rest-api/releases/tag/v1.0.0
