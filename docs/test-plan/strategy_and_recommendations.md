# Strategy & Recommendations

## Part C - Summary

Answers to the take-home prompts in `docs/specs/HQA_Take_Home_Task.md`. The broader test strategy for this feature is in [Appendix A](#appendix-a-test-strategy-for-single-bet-placement).

### 1. Why these two automated tests

| Required test | Scenario | Rationale |
|---|---|---|
| **UI E2E** | [TC-01](TP-001_single_bet_placement.md#tc-01---happy-path-place-a-valid-single-bet-e2e) | Core revenue flow: odds → bet slip → place → receipt. Money moves across header, bet slip, and receipt in one flow - highest business impact if broken. |
| **API** | [TC-01b](TP-001_single_bet_placement.md#tc-01b---happy-path-place-a-valid-bet-via-api-contract--money-math) | `POST /api/place-bet` is the financial source of truth. Direct API check is faster and more stable than UI; pins contract fields, `payout = stake × odds`, and persisted balance. Isolates backend defects from frontend rendering issues. |

**TC-02 (insufficient balance) - critical, always in scope**

I consider [TC-02](TP-001_single_bet_placement.md#tc-02---insufficient-balance-is-rejected-no-over-charge) a **release-blocking** check and would verify it in any case - manually in the top-3 execution, and via automation (`test_place_bet_rejects_overdraft`, xfail on [API-005](../defects/api/API-005_overdraft_negative_balance.md)). In an ideal pairing with UI TC-01, the required API automation would be this negative guardrail, not a second happy path: UI proves the flow works; API proves money cannot leave the platform.

**Why TC-01b is the required API test instead**

- With [API-005](../defects/api/API-005_overdraft_negative_balance.md) open, TC-02 cannot pass - using it as the sole required gate would mark the main automation red on every run. TC-01b stays green and demonstrates contract + money math while the product is broken.
- TC-01b still adds value UI cannot replace: it isolates backend `payout` / `balance` math and persisted state without receipt rendering in the way.

**Other scenarios not chosen as required**

- **TC-03** (late bet) is blocked in this sandbox: `kickoffDate` is date-only (no time/timezone), so reliable reproduction is not feasible - see [API-008](../defects/api/API-008_bet_on_completed_match.md) and manual execution in [execution summary](execution_summary.md).

**Exploratory automation** (beyond the two required tests): TC-02 overdraft, payload validation, HTTP protocol, currency xfails - `tests/api/bets/test_bets.py`; UI - `tests/ui/`.

### 2. Intentionally manual

| Area | Examples | Why manual |
|---|---|---|
| UI resilience | Button lock during `Placing…`, error modals, network delay | Transient states → flaky automation; better caught by exploratory session |
| Concurrency | TC-08 simultaneous requests | Needs isolated users + API-005 fix; deferred |
| Filters & UX | TC-07 date/odds filters, invalid range feedback | Spec gaps ([SPEC-006](../defects/specs/SPEC-006_filters_no_api_contract.md)); UX judgement |
| Late-bet UI handling | TC-03 E2E error path | Sandbox date-only constraint; API side validated manually via completed-match bet |

### 3. Top recommendations if scaling

1. **Test data & isolation** - per-run user provisioning and `set-balance(amount)` instead of shared `SPORTY_TEST_USER_ID` + drain-via-bets; enables parallel CI.
2. **Contract guard in CI** - OpenAPI ↔ Pydantic drift check + Schemathesis smoke on `api/openapi.json` on every PR.
3. **UI execution infrastructure** - **Docker images** with pinned browser/driver versions and **Selenium Grid** or a cloud provider for reproducible, parallel UI runs across environments and browser versions.
4. **UI tooling evaluation** - this submission uses **Selenium WebDriver** per assignment requirements. At scale, compare candidates (e.g. Playwright, Selenium with BiDi) on:
   - **Cost of migration** vs gains in stability, execution speed, and debug time - including built-in diagnostics (trace, video, screenshots on failure) and less time lost to flaky waits or driver/browser version drift in CI.
   - **Fit for this product** - network interception, reliable handling of async UI states, and smooth CI integration.
   - **Team maintenance** - can the team write and fix tests without the framework becoming a bottleneck; tooling that speeds up authoring and debugging (e.g. codegen, trace viewer, inspector); how easily the suite scales to parallel runs and additional browsers without rework.

   Migrate only when the numbers justify it. Regardless of stack: thin UI smoke on every PR, full E2E on release candidates.

---

## Appendix A: Test Strategy for Single Bet Placement

Scope: highest-priority risks for this feature in a sports betting product. Not an exhaustive test catalogue.

**Context.** In sports betting, smooth UX and UI consistency matter for retention, but the API is the financial core. Frontend bugs frustrate users; backend logic flaws cause direct money loss - and scale quickly when concurrency or contract gaps are involved. The strategy below is risk-prioritised: financial correctness and API contracts first, cosmetic UI issues second.

### Phase 0: Before implementation

- Review the spec for gaps and contradictions (e.g. missing late-bet cutoff, undefined concurrent-request behaviour).
- Align with interested parties on `SPEC` findings before code is written.

### Block 1: UI and core E2E

Focus: bet placement works end-to-end and the UI does not distort what the user intended.

- **Happy path:** odds selection → bet slip → place → receipt; receipt values match what the user saw before placement.
- **Request payload:** verify the frontend transmits exactly what the user selected - stake, `matchId`, and outcome. Watch for stake distortion, `matchId` manipulation, and precision/rounding errors when the placement request is built.
- **Resilience:** error modals for 4xx/5xx; Place button locked during in-flight requests (no misclicks or double-submit); UI recovers after failure without hanging.

### Block 2: Backend and money

- Balance rules: no overdraft, min/max stake enforced, `payout = stake × odds`.
- Concurrency: no double-spend on parallel requests.
- Late bets: reject bets after kickoff.

  > **Sandbox note.** Odds are static for the session (acceptable for this assignment). In production, odds are validated at placement time. Here, `kickoffDate` is date-only with no time/timezone, so automated late-bet checks are unreliable - see [API-008](../defects/api/API-008_bet_on_completed_match.md). In a real environment this would be a Block 2 priority.

**No-Go rule.** Failures in Blocks 1 or 2 on money movement, API contracts, or concurrency stop testing - fix the financial core first.

### Block 3: Extended coverage (after Blocks 1–2 pass)

Once the financial core is solid, work through the rest of the specification in more depth - frontend and backend edge cases not yet covered in Blocks 1–2 - and run additional exploratory sessions around the bet placement flow. Beyond that functional pass, expand into domain-specific quality dimensions:

- **Security:** authentication and authorization on API routes; classic web vulnerabilities - cross-site scripting (XSS), SQL injection (SQLi), insecure direct object reference (IDOR, e.g. placing a bet against another user's balance).
- **Fuzzing:** send malformed, unexpected, and oversized payloads to `place-bet` and related endpoints; confirm the service returns controlled errors instead of 500s or crashes.
- **Load:** stress the API under sharp traffic spikes - in live betting, bet volume often peaks in the minutes before kickoff.
- **Database:** transaction isolation under concurrent writes (no lost updates on balance); audit logs complete and immutable enough to settle user disputes.
- **Compliance:** geolocation blocks bets from restricted jurisdictions; KYC gates (age/identity) before real-money play; responsible gaming - deposit/loss limits, cooling-off periods, self-exclusion registers enforced on placement.
- **Payments (PSPs):** deposits and withdrawals through external payment providers; timeout/retry handling without double-billing; ledger reconciliation between the PSP and the internal wallet.
- **UI:** cross-browser behaviour, layout on non-standard viewports, accessibility (keyboard navigation, screen readers, contrast).

### Block 4: Automation and production

- **Pyramid:** unit and integration tests on backend; component tests on bet slip logic; API contract checks; UI E2E only for core flows (see [§3](#3-top-recommendations-if-scaling)).
- **CI gates:** fast checks on every PR; heavier API and E2E on release candidates; failed gate blocks merge.
- **Observability:** alert on spikes in `POST /api/place-bet` 4xx/5xx vs baseline - catches integration issues sandbox tests miss.
