# Manual Execution Summary (Part A.2)

Top **3 highest-priority** scenarios from [TP-001](TP-001_single_bet_placement.md), executed manually against the live app, plus brief exploratory notes.

**Environment:** Chrome desktop, `https://qae-assignment-tau.vercel.app/?user-id=<user-id>`, balance reset via `POST /api/reset-balance` between runs.

## Top 3 scenarios

| ID | Scenario | Result | Key findings |
|---|---|---|---|
| **TC-01** | Happy path: place a valid single bet (E2E) | **Fail** (known defects) | Flow completes, but receipt and list have issues: [UI-010](../defects/ui/UI-010_receipt_missing_info.md) (missing selection/time, wrong team order), [UI-012](../defects/ui/UI-012_wrong_payout_receipt.md) (payout hardcoded `stake × 2`), [UI-001](../defects/ui/UI-001_past_matches_shown.md) (past matches in list), [UI-011](../defects/ui/UI-011_overdraft.md) (balance not refreshed after bet) |
| **TC-02** | Insufficient balance rejected | **Fail** | Overdraft succeeds instead of rejection: [API-005](../defects/api/API-005_overdraft_negative_balance.md) (balance goes negative), [UI-011](../defects/ui/UI-011_overdraft.md) (UI keeps allowing bets on stale balance). Status code under-specified: [SPEC-004](../defects/specs/SPEC-004_insufficient_balance_status_undefined.md) |
| **TC-03** | Late bet on completed match rejected | **Fail** | `POST /api/place-bet` accepts bets on completed matches: [API-008](../defects/api/API-008_bet_on_completed_match.md). UI shows finished matches as bettable: [UI-001](../defects/ui/UI-001_past_matches_shown.md). Reliable kickoff-time E2E blocked by date-only API field: [SPEC-002](../defects/specs/SPEC-002_kickoff_datetime_vs_date.md) |

**Verdict:** Feature is **No-Go** for release - critical money-safety and receipt defects. Full reports: `docs/defects/`.

## Exploratory notes (ad-hoc, ~15 min)

Additional checks around the bet-placement flow surfaced further issues - not all automated:

| Area | Finding | Report |
|---|---|---|
| API contract | `currency: "USD"` on place-bet | [API-006](../defects/api/API-006_place-bet_currency_usd.md) |
| API protocol | `GET /api/place-bet` returns 200 | [API-004](../defects/api/API-004_place-bet_get_not_blocked.md) |
| Reset harness | Reset response ≠ persisted GET balance | [API-007](../defects/api/API-007_reset-balance_persisted_inconsistent.md) |
| Filters | Odds/date filter edge cases, counter, invalid input | [UI-004](../defects/ui/UI-004_odds_min_not_inclusive.md) – [UI-008](../defects/ui/UI-008_filter_counter_not_updated.md) |
| Spec gaps | Min stake contradiction, payout rounding undefined | [SPEC-001](../defects/specs/SPEC-001_min_stake_contradiction.md), [SPEC-003](../defects/specs/SPEC-003_payout_rounding_undefined.md) |

Some of these are covered by exploratory API automation in `tests/api/bets/test_bets.py` (xfail where broken).

## Automation mapping

| Manual scenario | Automated? | Location |
|---|---|---|
| TC-01 | Yes (required) | `tests/ui/bets/test_place_bet.py` |
| TC-01b | Yes (required) | `tests/api/bets/test_bets.py::test_place_bet_success` |
| TC-02 | Exploratory xfail | `tests/api/bets/test_bets.py::test_place_bet_rejects_overdraft` |
| TC-03 | Manual + defect doc | [API-008](../defects/api/API-008_bet_on_completed_match.md) |


## Test artifacts
The most noticeable defects observed for Single Bet Placement feature are listed in `docs/defects/` as individual files (UI, API, Spec). Among these, the most significant are grouped below by layer, ordered by severity.

#### Release-Blocking Issues (No-Go)
Any hard acceptance failure on money movement or API contracts marks the feature **No-Go**. The defects below are the most serious and must be fixed before release:

* **[API-008](../defects/api/API-008_bet_on_completed_match.md) (Critical)** - `POST /api/place-bet` accepts bets on already-completed matches (no lifecycle/start-time guard). Direct financial and legal exposure.
* **[API-005](../defects/api/API-005_overdraft_negative_balance.md) (Critical)** - Overdraft allowed: a stake exceeding the balance succeeds and drives the balance negative with no lower bound; `insufficient_balance` is never returned. Directly reached from [UI-011](../defects/ui/UI-011_overdraft.md).
* **[UI-011](../defects/ui/UI-011_overdraft.md) (Critical)** - The UI does not refresh the balance after placement, so it keeps sending bets once the real server-side balance is already insufficient (the frontend facet of API-005).
* **[UI-010](../defects/ui/UI-010_receipt_missing_info.md) (High)** - Bet receipt omits match date/time, selection, and exact timestamp, and shows Home/Away in the wrong order.
* **[UI-012](../defects/ui/UI-012_wrong_payout_receipt.md) (High)** - Receipt "Potential Payout" is hardcoded to `stake × 2`, ignoring the real odds and the correct `payout` from `/place-bet`.

The remaining quality and compliance issues (financial precision, contract/spec gaps, UI filters, etc.):

**UI (Frontend) - `docs/defects/ui/`**
* **[UI-001](../defects/ui/UI-001_past_matches_shown.md) (High; becomes Critical with [API-008](../defects/api/API-008_bet_on_completed_match.md))** - Match list shows past matches as bettable (API returns old data; UI renders it).
* **[UI-002](../defects/ui/UI-002_no_kickoff_time.md) (High)** - Match List does not show kickoff time (spec mandates date/time; API returns date only; UI still does not render time even when a full datetime is mocked).
* **[UI-004](../defects/ui/UI-004_odds_min_not_inclusive.md) (Medium)** - Odds filter MIN is exclusive, contradicting the documented inclusive boundary.
* **[UI-007](../defects/ui/UI-007_odds_min_gt_max.md) (Medium)** - Invalid odds range (MIN > MAX, including crossed sliders) accepted with no error/feedback.
* **[UI-008](../defects/ui/UI-008_filter_counter_not_updated.md) (Medium)** - Result counter always shows the total match count, ignoring the active filter.
* **[UI-003](../defects/ui/UI-003_matches_not_sorted.md) (Low)** - Match list has no deterministic order; kickoff dates do not ascend (spec does not define a sort order).
* **[UI-005](../defects/ui/UI-005_odds_max_undefined.md) (Low)** - Odds filter MAX semantics undefined across the three-outcome market of a match (keep if any/all odds within bound); no feedback on retained/removed matches.
* **[UI-006](../defects/ui/UI-006_odds_filter_invalid_input.md) (Low)** - Odds MIN/MAX fields accept unsupported symbols (e.g. `E`, `+`) with no length limit and no clear feedback; invalid input is silently dropped on apply, so filtering still works.
* **[UI-009](../defects/ui/UI-009_stake_overflow.md) (Low)** - Bet slip accepts an over-large stake, overflowing/breaking the "Total Stake" and "Potential Payout" display; the Place Bet button is disabled for out-of-range input, so it does not reach placement.

**API (Backend) - `docs/defects/api/`**
* **[API-006](../defects/api/API-006_place-bet_currency_usd.md) (High)** - `POST /api/place-bet` returns `currency: "USD"` instead of `"EUR"`, contradicting every other endpoint and the spec; misleads clients/users on a financial response.
* **[API-007](../defects/api/API-007_reset-balance_persisted_inconsistent.md) (Medium)** - `reset-balance` responds with `balance: 125.5` but `GET /api/balance` returns `120` (€5.50 mismatch). Test-only endpoint; tests work around it by reading the actual balance.
* **[API-001](../defects/api/API-001_place-bet_500_error.md) (Medium/High)** - `500` on a raw binary null-byte payload instead of `400`; unhandled exception / potential DoS vector.
* **[API-003](../defects/api/API-003_missing_allow_header_405.md) (Medium)** - `405` responses omit the required `Allow` header (RFC 9110 §15.5.6).
* **[API-004](../defects/api/API-004_place-bet_get_not_blocked.md) (Medium)** - `GET /api/place-bet` returns `200 OK` (empty body) instead of `405 Method Not Allowed`, diverging from the other endpoints and the advertised `POST, OPTIONS` methods.
* **[API-002](../defects/api/API-002_stake_precision_422_mismatch.md) (Low)** - OpenAPI contract mismatch: `stake` schema lacks `multipleOf` (and boundary) constraints, so high-precision floats pass contract validation but fail backend rules.

**Spec - `docs/defects/specs/`**
* **[SPEC-001](../defects/specs/SPEC-001_min_stake_contradiction.md) (High)** - Contradictory minimum stake value (Business Rules/UI copy say €1.00; Stake Validation says €1.01) - dangerous ambiguity that can propagate into an incorrect implementation.
* **[SPEC-004](../defects/specs/SPEC-004_insufficient_balance_status_undefined.md) (Medium)** - "Insufficient balance" has no explicit HTTP status mapping (422 vs 409 vs 402), so negative tests cannot assert a code and clients cannot distinguish it reliably.
* **[SPEC-002](../defects/specs/SPEC-002_kickoff_datetime_vs_date.md) (Medium)** - Kickoff "date/time" required by the UI, but `GET /api/matches` documents `kickoffDate` as `YYYY-MM-DD` (date only) - root cause of [UI-002](../defects/ui/UI-002_no_kickoff_time.md).
* **[SPEC-003](../defects/specs/SPEC-003_payout_rounding_undefined.md) (Medium)** - Payout precision/rounding rule undefined (`stake × odds` often yields >2 decimals); UI, receipt, and API could each round differently.
* **[SPEC-006](../defects/specs/SPEC-006_filters_no_api_contract.md) (Medium)** - Filters (date/odds) defined for the UI but no `GET /api/matches` query-parameter/contract defined (inclusivity, invalid-range error) - root cause of UI-004/005/006/007/008.
* **[SPEC-005](../defects/specs/SPEC-005_bet_in_progress_409_undefined.md) (Medium)** - "Bet already in progress" (409) lifecycle undefined - no deterministic way to trigger or clear the state.
* **[SPEC-007](../defects/specs/SPEC-007_odds_static_for_session_ambiguous.md) (Low)** - "Odds static for session" is ambiguous (which "session", what stability window).
* **[SPEC-008](../defects/specs/SPEC-008_selection_1x2_mapping_undocumented.md) (Low)** - UI `1/X/2` vs API `HOME/DRAW/AWAY` mapping is only documented in the Domain Context prose (HQA), not in the formal API contract/selection-validation sections.
