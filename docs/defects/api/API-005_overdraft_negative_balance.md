# Bug ID: API-005 - Overdraft Allowed: Bet Exceeding Balance Succeeds and Drives Balance Negative

* **Severity:** Critical (users can bet money they do not have)
* **Reproduction Steps:**
  The specification requires that a stake must not exceed the available balance and must be rejected as "insufficient balance". In practice, the backend accepts bets larger than the current balance and lets the balance go **negative without any lower bound**. The `insufficient_balance` error is never returned.

  1. Reset the balance and drain it below the max stake:
     ```bash
     U='candidate-BqxxUlex26'
     B='https://qae-assignment-tau.vercel.app'
     curl -s -X POST -H "x-user-id: $U" "$B/api/reset-balance"
     # place a max-stake bet to reduce the remaining balance (e.g. to ~20)
     curl -s -X POST -H "x-user-id: $U" -H 'Content-Type: application/json' \
       -d '{"matchId":"premier-league-manutd-chelsea","selection":"HOME","stake":100}' \
       "$B/api/place-bet"
     ```
  2. Place another bet whose stake exceeds the remaining balance:
     ```bash
     curl -s -X POST -H "x-user-id: $U" -H 'Content-Type: application/json' \
       -d '{"matchId":"premier-league-manutd-chelsea","selection":"HOME","stake":100}' \
       "$B/api/place-bet"
     ```
  3. Check the balance:
     ```bash
     curl -s -H "x-user-id: $U" "$B/api/balance"
     ```

* **Expected Result:**
  The second bet must be rejected with `422 Unprocessable Entity` and the error `insufficient_balance`. The balance must remain unchanged (the rejected stake is not deducted) and must never become negative.

* **Actual Result:**
  The bet succeeds with `200 OK`, the stake is deducted, and the balance becomes negative. Repeating the request keeps decreasing it without any limit:
  ```text
  balance 20  -> bet 100 -> {"...","balance":-80,"currency":"USD"}
  balance -80 -> bet 100 -> {"...","balance":-180,"currency":"USD"}
  ```

* **Business Impact:**
  Direct financial loss and data integrity failure: customers can place bets far beyond their funds, and the ledger goes into an impossible negative state. This is the highest-impact defect in the betting flow.

* **Note:** Covered by automated tests (both currently `xfail` pending the fix):
  * `tests/api/bets/test_bets.py::TestPlaceBet::test_place_bet_rejects_overdraft`
  * `tests/api/bets/test_bets.py::TestPlaceBet::test_place_bet_balance_never_goes_negative`

   Related spec gap: [SPEC-004](../specs/SPEC-004_insufficient_balance_status_undefined.md).

   Related UI defect: [UI-011](../ui/UI-011_overdraft.md) - the UI does not refresh the balance after a bet, so the user can keep sending bets even once the real balance is insufficient, making overdraft easy to trigger from the UI.
