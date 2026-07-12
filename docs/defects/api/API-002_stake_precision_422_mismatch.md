# Bug ID: API-002 - API Contract Mismatch: OpenAPI Schema Missing 'multipleOf' Constraint for Stake Precision

* **Severity:** Low
* **Reproduction Steps:**
  The server's business logic correctly restricts the `stake` field to 2 decimal places. However, because the public `openapi.json` specification defines `stake` as a generic `number` without limitations, automated tools like Schemathesis generate high-precision floats that violate the backend's expectations but fully satisfy the API contract.
  
  To reproduce the contract mismatch manually:
  1. Send a bet placement request with a high-precision float:
     ```bash
     curl -X POST \
       -H 'x-user-id: candidate-BqxxUlex26' \
       -H 'Content-Type: application/json' \
       -d '{"matchId": "serie-a-napoli-lazio", "selection": "AWAY", "stake": 26.979506461666013}' \
       https://qae-assignment-tau.vercel.app/api/place-bet
     ```

* **Expected Result:**
  The public API contract (`openapi.json`) must accurately mirror the strict backend Business Rules ("Stake precision: Up to 2 decimal places"). 
  
  To stop fuzzers and clients from generating stakes the API will reject, add `multipleOf: 0.01` to the `stake` schema.

  * Add `multipleOf: 0.01` (required).
  * Optionally add `minimum: 1.00` and `maximum: 100.00` if limits are fixed; leave bounds open if they are config-driven.

  *Target Schema Fix (Option A Example):*
  ```yaml
  stake:
    type: number
    multipleOf: 0.01
    minimum: 1.00
    maximum: 100.00

 * Note: While the `openapi.json` specification currently lacks these constraints, existing backend-side validation handles the precision and bet limits internally.
