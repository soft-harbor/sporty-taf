# Bug ID: API-007 - reset-balance Response Inconsistent With Persisted State (125.5 vs 120)

* **Severity:** Medium (contract consistency; test-only endpoint, low product impact)
* **Reproduction Steps:**
  The specification states that after a reset "Response body and persisted state must be consistent" and the initial balance is €125.50. In practice, `reset-balance` responds with `balance: 125.5`, but a subsequent `GET /api/balance` returns `120`.

  1. Reset the balance and immediately read it back:
     ```bash
     U='candidate-BqxxUlex26'
     B='https://qae-assignment-tau.vercel.app'
     curl -s -X POST -H "x-user-id: $U" "$B/api/reset-balance"   # -> balance 125.5
     curl -s -H "x-user-id: $U" "$B/api/balance"                 # -> balance 120
     ```
  2. Repeat - the result is stable and reproducible:
     ```text
     reset -> 125.5  | GET balance -> 120
     reset -> 125.5  | GET balance -> 120
     reset -> 125.5  | GET balance -> 120
     ```

* **Expected Result:**
  After reset, `GET /api/balance` must equal the value returned by `reset-balance`(and equal the configured initial balance of €125.50).

* **Actual Result:**
  The reset response reports `125.5`, but the persisted balance is `120` - a reproducible €5.50 discrepancy. Subsequent bets are deducted from `120`, not `125.5`.

* **Business Impact:**
  `reset-balance` reports `125.5` but `GET /api/balance` returns `120`, so any flow that assumes €125.50 after reset starts from the wrong amount. Tests work around this by reading the actual balance via `GET /api/balance`.

* **Note:** Covered by
  `tests/api/balance/test_balance_reset.py::TestBalanceResetAPI::test_reset_balance_persists_state` (currently `xfail` pending the fix). Because of this bug, tests read the actual balance via `GET /api/balance` instead of assuming 125.5.
