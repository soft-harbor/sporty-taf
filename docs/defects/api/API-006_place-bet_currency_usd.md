# Bug ID: API-006 - place-bet Response Returns currency "USD" Instead of "EUR"

* **Severity:** High (Incorrect currency on a financial response - misleads clients and users)
* **Reproduction Steps:**
  The platform currency is EUR (€): the Business Rules, the Domain Context, and the `GET /api/balance` and `POST /api/reset-balance` responses all use `EUR`. However, `POST /api/place-bet` returns `currency: "USD"`.

  1. Reset the balance and place a valid bet:
     ```bash
     U='candidate-BqxxUlex26'
     B='https://qae-assignment-tau.vercel.app'
     curl -s -X POST -H "x-user-id: $U" "$B/api/reset-balance"
     curl -s -X POST -H "x-user-id: $U" -H 'Content-Type: application/json' \
       -d '{"matchId":"premier-league-manutd-chelsea","selection":"HOME","stake":10}' \
       "$B/api/place-bet"
     ```
  2. Compare with the balance endpoint:
     ```bash
     curl -s -H "x-user-id: $U" "$B/api/balance"
     ```

* **Expected Result:**
  `POST /api/place-bet` returns `currency: "EUR"`, consistent with the specification and with every other endpoint.

* **Actual Result:**
  ```json
  {"message":"Bet placed successfully","matchId":"premier-league-manutd-chelsea","selection":"HOME","stake":10,"odds":2.45,"payout":24.5,"balance":110,"currency":"USD"}
  ```
  while `GET /api/balance` for the same user returns `{"balance":110,"currency":"EUR"}`.

* **Business Impact:**
  A financial response with the wrong currency can mislead any client that displays the receipt after placement.

* **Note:** Covered by
  `tests/api/bets/test_bets.py::TestPlaceBet::test_place_bet_currency_is_eur` (currently `xfail` pending the fix).
