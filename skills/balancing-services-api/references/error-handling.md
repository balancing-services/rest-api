# Error handling

## Problem body

Errors come back as RFC 7807 Problem Details with content type `application/problem+json`:

```json
{
  "type": "invalid-parameter",
  "title": "Invalid Parameter",
  "status": 400,
  "detail": "The area parameter value is not valid"
}
```

`type`, `title` and `status` are always present; `detail` is optional and describes the specific
occurrence. `detail` is written for humans — log it, show it, but never branch on its wording.

## Known `type` values

| `type` | Status | Meaning | Retry? |
|---|---|---|---|
| `missing-parameter` | 400 | A required query parameter was not supplied | No — fix the request |
| `invalid-parameter` | 400 | A parameter value is not valid (bad area, unparseable timestamp, `limit` out of range, malformed `cursor`) | No — fix the request |
| `unauthorized` | 401 | Missing, malformed, expired or revoked token | No |
| `forbidden` | 403 | The token is valid but does not permit access to the requested data | No |
| `not-found` | 404 | The requested resource does not exist | No |
| `rate-limited` | 429 | Request limit for the token exceeded | Yes — see below |
| `not-implemented` | 501 | The feature is not available yet | No |
| `internal-error` | 500 | Unexpected server-side failure | Yes, with backoff |

**`type` is an open set.** New values may be introduced without a major-version bump. Match the
values you handle explicitly and fall back on `status` for anything you do not recognise; an unknown
`type` must never make the client raise. Do not generate a closed enum from it, and do not assert
exhaustiveness in a `switch`/`when` over it.

## Rate limiting

A 429 response carries two headers documented in the spec:

- `Retry-After` — seconds to wait before retrying.
- `X-RateLimit-Limit` — the requests-per-minute allowance for your token.

Honour `Retry-After` when present rather than inventing a delay. If it is absent, fall back to
exponential backoff with jitter. Assume parallel workers sharing one token share one budget —
either serialise the drain or cap concurrency.

Rate limits are the usual reason a long drain fails part-way. Retry the failed page with the same
cursor rather than restarting the drain.

## Retry guidance

Every endpoint is a read-only `GET`, so retries are always safe — there is nothing to make
idempotent.

Retry: 429 (per `Retry-After`), 500, and transport-level failures (connection resets, timeouts).
Three or four attempts with exponential backoff and jitter is a reasonable ceiling; beyond that the
problem is unlikely to clear on its own.

Do not retry 400, 401, 403, 404 or 501 — the same request will fail the same way. Surface these with
`type` and `detail` so the cause is visible.

Two cases that look like errors but are not:

- **An empty `data` array is a success.** Data exists only where the underlying source publishes
  it: an area/dataset combination with no data returns 200 with `data: []`, not 404. Do not
  escalate it.
- **A rejected cursor is a client bug, not a transient fault.** Recover by restarting the drain
  with no `cursor`; retrying the same cursor cannot succeed. A 400 does not machine-readably say
  *which* parameter was bad (`detail` is not for branching), so use the request as the discriminator: if it
  carried a `cursor`, restart the drain without one — at most once, so a genuinely bad parameter
  still fails fast; if it did not, the request itself is wrong.

## With the Python client

`sync_detailed` (and its async counterpart) returns a response object carrying `status_code` and the
parsed body, so error handling stays in normal control flow:

```python
response = get_imbalance_prices.sync_detailed(client=client, area="EE", ...)

if response.status_code == 200:
    handle(response.parsed)
elif response.status_code == 429:
    wait(int(response.headers.get("Retry-After", 5)))
elif response.parsed is not None:
    problem = response.parsed          # Problem model
    log.error("%s (%s): %s", problem.title, problem.type, problem.detail)
else:
    # Undocumented status (a 502/503 from an intermediary, say): no Problem body was parsed
    log.error("HTTP %s: %s", response.status_code, response.content)
```

On statuses the spec does not document, the generated client leaves `parsed` as `None` — fall back
to `status_code` and the raw body rather than assuming a Problem model.

`problem.type` is a plain string on v2 — compare it as a string, and keep a `status_code` fallback
for unrecognised values. Setting `raise_on_unexpected_status=True` on the client makes undocumented
status codes raise `UnexpectedStatus` instead of returning; leave it off if you prefer to branch on
`status_code` yourself.

See `clients/python/examples/error_handling.py` in this repository for a full retry example.
