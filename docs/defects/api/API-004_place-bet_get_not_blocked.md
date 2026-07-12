# Bug ID: API-004 - GET /api/place-bet Returns 200 Instead of 405 Method Not Allowed

* **Severity:** Medium
* **Reproduction Steps:**
  The `POST /api/place-bet` endpoint correctly rejects most unsupported methods (`PUT`, `DELETE`, `TRACE` all return `405`), but a `GET` request to the same path is not blocked and returns `200 OK`.

  1. Send a `GET` request to the placement endpoint and inspect the response:
     ```bash
     curl -i -X GET -H 'x-user-id: candidate-BqxxUlex26' \
       https://qae-assignment-tau.vercel.app/api/place-bet
     ```

* **Expected Result:**
  Per the Feature Specification ("Unsupported HTTP method → Return method-not-allowed response"), a `GET` on a POST-only resource must return `405 Method Not Allowed`. The server itself advertises the allowed methods as `POST, OPTIONS` (see the `access-control-allow-methods` header), so `GET` should be rejected.

* **Actual Result:**
  The server returns `200 OK` with an empty JSON body `{}`, while still advertising only `POST, OPTIONS` as allowed methods:
  ```text
  HTTP/2 200
  access-control-allow-methods: POST, OPTIONS
  content-type: application/json; charset=utf-8
  content-length: 2

  {}
  ```

* **Business Impact:**
  A client sending `GET` by mistake gets `200` instead of `405`, so the error is easy to miss. Other endpoints (`/api/balance`, `/api/matches`, `/api/reset-balance`) correctly return `405` for unsupported methods.

* **Note:** Covered by the automated test
  `tests/api/bets/test_bets.py::TestBetsPlaceProtocol::test_place_bet_get_not_allowed`(currently `xfail` pending this fix).
