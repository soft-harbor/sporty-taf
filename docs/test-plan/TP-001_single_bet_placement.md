# Test Plan - Single Bet Placement (TP-001)

## Scope & Approach

This plan covers the **Single Bet Placement** feature (desktop web, football, pre-match, single bet only). It contains a focused, prioritized set of scenarios spanning **happy path**, **negative / validation**, and **boundary** cases.

Scenarios are described **by intent**: the layer noted for each scenario (UI E2E / API / both) reflects where the risk is best exercised, not an exhaustive  matrix. Money-handling and state integrity are treated as the highest business risk and drive prioritization.

**References:**

- `docs/specs/Feature_Specification.md`
- `docs/specs/HQA_Take_Home_Task.md` (Domain Context)
- Known spec ambiguities: `docs/defects/specs/SPEC-00*`

**Environment:**

- App: `https://qae-assignment-tau.vercel.app/?user-id=<user-id>`
- Auth (API): header `x-user-id: <user-id>`
- Browser: latest desktop Chrome

**Baseline test data / business rules:**

- Initial balance: **€125.50**
- Stake: min **€1.00**, max **€100.00**, precision **up to 2 decimals** (see SPEC-001)
- Odds range: **1.01 – 1000.00**, static for session
- Currency: EUR (€)
- `POST /api/reset-balance` is used to return balance to its initial value between runs so tests are deterministic.

**Priority legend:** Critical / High / Medium / Low.

---

## TC-01 - Happy path: place a valid single bet (E2E)

- **Priority:** Critical
- **Layer:** UI E2E (backed by API state checks)
- **Type:** Happy path
- **Risk Rationale:** This is the core revenue flow. It exercises money movement end-to-end (stake deduction, payout calculation, balance consistency across header / bet slip / receipt). A defect here has the highest business impact - wrong charge, wrong payout, or inconsistent balance directly affects customer money.
- **Preconditions:** Balance reset to €125.50; at least one upcoming match available.
- **Steps:**
  1. Open the app with a valid `user-id`.
  2. Note the initial balance shown in the header.
  3. Pick a match and click one odds button (`1` / `X` / `2`); note the odds value.
  4. Confirm the bet slip shows the selection, the odds, and updates the potential payout as the stake is entered.
  5. Enter a valid stake (e.g. €10.00).
  6. Verify the displayed potential payout equals `stake × odds`.
  7. Click **Place Bet** and wait for the flow to resolve.
- **Expected Result:**
  - Button shows a loading state (`Placing...`) and resolves to a single outcome.
  - Success **receipt** appears showing: Bet ID, match details, selection, stake, odds at placement, potential payout, and placement timestamp.
  - Receipt values match what was shown before placement (odds, stake, payout).
  - Balance is reduced by exactly the stake (`125.50 − 10.00 = 115.50`) and is **consistent** in the header and bet slip.
  - Closing the receipt returns to the main flow with **no active selection**.

---

## TC-01b - Happy path: place a valid bet via API (contract & money math)

- **Priority:** Critical
- **Layer:** API
- **Type:** Happy path
- **Risk Rationale:** The `POST /api/place-bet` response is the source of truth for the money math and is consumed by any client. Validating it directly (not only through the UI) is faster, more stable, and pins the contract: response fields, `payout = stake × odds`, and the returned `balance` after deduction. It complements the UI flow (TC-01) at the API layer and isolates whether a money defect is backend or frontend.
- **Preconditions:** Reset balance to €125.50; obtain a valid `matchId` and its `odds` from `GET /api/matches`.
- **Steps:**
  1. `POST /api/reset-balance` and confirm balance is €125.50.
  2. `GET /api/matches`; pick a match and record `matchId` and the odds for the chosen `selection`.
  3. `POST /api/place-bet` with header `x-user-id`, body `{ matchId, selection, stake }` (e.g. stake `10.00`).
  4. `GET /api/balance` to confirm the persisted balance.
- **Expected Result:**
  - Response `200` with body containing `message`, `matchId`, `selection`, `stake`, `odds`, `payout`, `balance`, `currency: "EUR"`.
  - `odds` in the response equals the odds from `GET /api/matches` for that selection (odds static for session, see SPEC-007).
  - `payout == stake × odds` (rounding rule pending SPEC-003).
  - `balance == 125.50 − stake` and matches the subsequent `GET /api/balance`(response and persisted state are consistent).
  - Echoed `matchId` / `selection` / `stake` equal the request.

---

## TC-02 - Insufficient balance is rejected (no over-charge)

- **Priority:** Critical
- **Layer:** Both
- **Type:** Negative (money safety)
- **Risk Rationale:** A user must never bet more than they hold or drive the balance negative. Because max stake (€100.00) is below the initial balance (€125.50), this state is only reachable after the balance has been drained - an easy-to-miss edge case with severe financial consequences. Note: the exact API status for this case is under-specified (see **SPEC-004**).
- **Preconditions:** Reduce balance below the intended stake, e.g. reset to €125.50, then place bets until the remaining balance is small (e.g. ~€5.00).
- **Steps:**
  1. Bring the balance down to a low value (e.g. €5.00).
  2. Select a match/outcome and enter a stake greater than the remaining balance but within the min/max rules (e.g. €10.00).
  3. Attempt to place the bet.
- **Expected Result:**
  - Placement is rejected with an "Insufficient balance" message.
  - The balance is **unchanged** (no deduction) and remains consistent across header and bet slip.
  - API returns a clear error status/body for the insufficient-balance case (exact code pending SPEC-004 clarification).

---

## TC-03 - Late bet: reject bets on matches in progress / completed (stale match state)

- **Priority:** Critical
- **Layer:** API (mandatory) + UI E2E (stale-state error handling)
- **Type:** Negative (money safety + correctness)
- **Risk Rationale:** The spec permits only pre-match/upcoming events (Section 1 "no live betting"; Section 3 "Upcoming matches only"). Accepting a bet on a match that has started or finished is a correctness and money-safety defect - the outcome may already be decided, or the event may be live. This check is also the primary guard against **stale UI state**: the match list is cached, an odds button can stay clickable after kickoff, and a user may attempt to place a bet on a match that has since started/finished. Because the spec defines no time cutoff and the API returns only a date (see the spec gap above / **SPEC-002**), this is the scenario most likely to be silently unenforced.
- **Preconditions:**
  - API: a match whose kickoff is in the past / in progress (the test must not rely on the date-only `kickoffDate` field alone, since it cannot express time; this precondition itself surfaces the **SPEC-002** gap).
  - UI: a match whose odds were rendered before kickoff and whose selection is kept after the match has started/finished (stale selection).
- **Steps:**
  - For API:
    1. `GET /api/matches`; obtain a match that is in progress or completed (kickoff <= now per a timezone-aware source).
    2. `POST /api/place-bet` for that match with a valid `selection` and a valid stake (within min/max and < balance).
    3. `GET /api/balance` to confirm the balance is unchanged by the rejected attempt.
  - For UI: 
    1. Keep a selection on a match that has since started/finished; click **Place Bet**.
    2. Observe how the error is surfaced and confirm no money moves.
- **Expected Result:**
  - API rejects the bet with a clear status/body (e.g. `409`/`422` with an explicit error type such as `match_not_available` / `match_closed`) and the **balance is unchanged** (no deduction, consistent with `GET /api/balance`).
  - API rejects regardless of stale client state - it must not trust a cached/old `kickoffDate`; the decision is made server-side from the real kickoff timestamp.
  - UI shows a **clear error** for the stale state - not a crash or an unhandled spinner. The generic "Something went wrong" modal (Section 2.5) is acceptable only if its body explains the match is no longer available; ideally a dedicated message (e.g. "This match has already started / finished" / "Betting is closed for this match").
  - The bet slip / selection is cleared or marked as unavailable; the user is **not charged**; the UI never stays stuck in the loading state.
- **Note:**
  - The app currently accepts this bet, that is a **Critical** defect caused by the missing time-window rule + **SPEC-002**; it must be filed and fixed before release.

---

## TC-04 - Stake boundary & precision validation

- **Priority:** High
- **Layer:** Both (UI messaging + API rejection)
- **Type:** Boundary + negative
- **Risk Rationale:** Stake limits are a hard business rule and a classic source of off-by-one/precision defects. The min-stake value is contradictory in the spec (€1.00 vs €1.01, see **SPEC-001**), so the boundary must be pinned down explicitly. Precision errors let malformed monetary amounts through (see **API-002**).
- **Preconditions:** Balance reset to €125.50 (enough to cover valid boundary bets).
- **Steps / data (enter stake, attempt placement):**
  1. `1.00` → at minimum (assumed inclusive per SPEC-001).
  2. `100.00` → at maximum.
  3. `1.9`, `99.1`, `25` → valid precision.
  4. `0.99` → below minimum.
  5. `100.01` → above maximum.
  6. `10.123` → 3 decimal places (invalid precision).
  7. `abc` / empty / null → non-numeric / missing.
  8. `0`, `-1` → zero / negative
- **Expected Result:**
  - `1.00`, `1.9`, `99.1`, `25` and `100.00` are **accepted**.
  - `0.99` → rejected with "Minimum stake is €1.00".
  - `100.01` → rejected with "Maximum stake is €100.00".
  - `10.123` → rejected for invalid precision (max 2 decimals).
  - `0`, `-1` → rejected with "Minimum stake is €1.00".
  - Non-numeric / empty → placement blocked; input rejects the value.
  - On the API layer, invalid values return `422` (semantic validation); the balance is **never** changed by a rejected attempt.

---

## TC-05 - API validation: selection, match & user context

- **Priority:** Medium
- **Layer:** API
- **Type:** Negative / contract
- **Risk Rationale:** The API must reject invalid payloads on its own, without relying on the UI. These are cheap, high-signal contract checks that catch malformed integrations and missing auth.
- **Preconditions:** Valid `user-id`; a known valid `matchId` from `GET /api/matches`.
- **Steps (each request to `POST /api/place-bet`, other fields valid):**
  1. `selection` = `"WIN"` (not in HOME/DRAW/AWAY).
  2. `matchId` missing / empty.
  3. `matchId` = unknown non-existent id.
  4. Omit the `x-user-id` header.
  5. Send a malformed / non-JSON body.
  6. Use an unsupported method (e.g. `GET`/`PUT` on `/api/place-bet`).
- **Expected Result:**
  - Invalid `selection` → `422`.
  - Missing/blank/unknown `matchId` → `422`.
  - Missing `x-user-id` → `401`.
  - Malformed body → `400` (currently a defect: raw null-byte causes `500`, see **API-001**).
  - Unsupported method → `405` with an `Allow` header (missing header is a defect, see **API-003**).
  - No balance change results from any rejected request.

> **Recommendation:** Good fit for schema-level contract validation with **Schemathesis** (optional `contract` dependency group in `pyproject.toml`, spec at `api/openapi.json`). A single run can probe invalid/missing fields, wrong types, malformed bodies, missing auth headers, unsupported methods, and response shape - fast feedback on contract drift before or alongside manual execution.

---

## TC-06 - Placement failure: error modal, Rebet & Close behavior

- **Priority:** Medium
- **Layer:** UI E2E
- **Type:** Negative / error handling
- **Risk Rationale:** Requirement 2.3 states the UI must always resolve to exactly one final outcome. A broken failure path (stuck spinner, silent failure, or a double charge on retry) is high-impact. This scenario verifies the recovery UX (Rebet / Close / X) and that a failed attempt does not move money.
- **Preconditions:** Ability to induce a placement failure (e.g. simulated server error / network failure via the failing condition available in the app or API).
- **Steps:**
  1. Select a match/outcome and enter a valid stake; note the balance.
  2. Trigger a placement that fails.
  3. Observe the error modal, then test **Rebet**.
  4. Repeat to failure, then test **Close** (and separately the top-right **X**).
- **Expected Result:**
  - Error modal appears titled "Something went wrong" with an explanatory body.
  - **Rebet** closes the modal and retries placement.
  - **Close** and **X** close the modal and clear the current selection/stake.
  - On failure, **no stake is deducted**; balance is unchanged and consistent.
  - The UI never remains stuck in the loading state.

---

## TC-07 - Filters: date range & odds range (inclusive), invalid range rejected

- **Priority:** Medium
- **Layer:** UI (with API contract check if filtering is server-side)
- **Type:** Boundary + validation
- **Risk Rationale:** Filters shape what a user can bet on; wrong inclusivity or a silently accepted invalid range gives misleading results. The API contract for filtering is undefined (see **SPEC-006**), so this also surfaces a spec gap.
- **Preconditions:** Multiple matches spanning several dates and a range of odds.
- **Steps:**
  1. Apply a single-day date filter; then an inclusive date range.
  2. Apply an odds min/max range and verify only matches within `[min, max]` show.
  3. Verify boundary matches (odds exactly equal to min or max) are included.
  4. Enter an invalid odds range (`min > max`).
- **Expected Result:**
  - Date filter returns matches for the selected day / inclusive range only.
  - Odds filter returns only matches within the inclusive range; boundary values are included.
  - Invalid range (`min > max`) is rejected with clear feedback and no misleading result set.

---

## TC-08 - Concurrent betting: balance & single-bet integrity under simultaneous requests

- **Status:** Not executed (deferred).
- **Priority:** Critical (once overdraft is blocked).
- **Layer:** API + white-box review (ideal).
- **Type:** Negative / concurrency / money safety.
- **Why deferred:** Moot while **API-005** (overdraft → negative balance) is open. A single sequential request can already overdraw, so a race condition adds nothing until the balance lower bound is enforced. Intentionally deferred until API-005 is fixed.
- **Scope (once unblocked):** Verify that `POST /api/place-bet` applies atomic read-check-and-deduct when multiple requests arrive simultaneously, preventing double-spend and negative balance. Note: spec does not forbid repeated bets on the same match; same-match concurrency is out of scope here (see **SPEC-005**).
- **Sub-scenarios (planned, not run):**
  - **TC-08a** - Sum exceeds balance: N concurrent requests on distinct matches, each individually valid but total > balance. Admitted bets must not exceed available funds; rest rejected with no money moved.
  - **TC-08b** - No negative / no double deduction: after burst, `GET /api/balance` must be `≥ 0` and equal `initial − Σ(admitted stakes)`; no duplicate/phantom bets.
- **Preconditions (planned):** Reset balance to €125.50. Use distinct `matchId`s with stakes so total overshoots balance while each stake is individually valid.
- **Steps (planned):**
  1. Fire concurrent batch at API layer (threads / parallel connections).
  2. Collect responses with statuses and balances.
  3. `GET /api/balance` for final persisted state.
  4. Inspect engine design: account-level locking or serializable transaction required; lock-free/eventually-consistent is a release blocker.
- **Expected Result (planned):**
  - Processor serializes requests; admitted stakes ≤ balance; rejected requests return clear insufficient-balance error and change nothing; final balance `≥ 0`.
  - White-box: confirm account locking or serializable isolation. If eventually-consistent, this is a release blocker once API-005 is fixed.
- **Blocking dependency:** **API-005**. Re-run only after balance lower bound and `insufficient_balance` rejection are enforced.

---

## Coverage summary

| ID | Title | Priority | Type | Layer | Defects |
| --- | --- | --- | --- | --- | --- |
| TC-01 | Happy path: place a valid single bet (E2E) | Critical | Happy path | UI E2E | UI-010, UI-012 (receipt issues; High), UI-001 (past matches in list) |
| TC-01b | Happy path: place a valid bet via API (contract & money math) | Critical | Happy path | API | API-006 (currency mislabel), SPEC-003 (payout rounding), SPEC-001 (min stake contradiction) |
| TC-02 | Insufficient balance is rejected (no over-charge) | Critical | Negative (money) | Both | API-005 (overdraft → negative balance, **No-Go**), UI-011 (stale balance, **No-Go**), SPEC-004 (status undefined) |
| TC-03 | Late bet: reject bets on matches in progress / completed (stale match state) | Critical | Negative (money + correctness) | API + UI E2E | API-008 (bet on completed match, **No-Go**), UI-001 (shows finished matches as bettable) |
| TC-04 | Stake boundary & precision validation | High | Boundary + negative | Both | API-002 (schema lacks precision/boundary), SPEC-001 (min stake), SPEC-003 (rounding) |
| TC-05 | API validation: selection, match & user context | Medium | Negative / contract | API | SPEC-008 (1X2↔HOME/DRAW/AWAY mapping), API-003/API-004 (method handling) |
| TC-06 | Placement failure: error modal, Rebet & Close behavior | Medium | Error handling | UI E2E | UI-011 (stale balance / in-flight state) |
| TC-07 | Filters: date range & odds range (inclusive), invalid range rejected | Medium | Boundary / validation | UI/API | UI-004, UI-005, UI-006, UI-007, UI-008, SPEC-006 (filter contract), SPEC-002 (kickoff date/time) |
| TC-08 | Concurrent betting: balance & single-bet integrity under simultaneous requests | Critical (not executed - deferred on API-005) | Negative / concurrency / money safety | API + white-box | API-005 (balance lower bound; blocked by open overdraft), SPEC-005 (in-progress lifecycle undefined) |
