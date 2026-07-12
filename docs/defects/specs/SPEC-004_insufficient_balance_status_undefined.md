# Spec Defect: SPEC-004 - "Insufficient Balance" Has No Explicit HTTP Status Mapping

* **Severity:** Medium (ambiguous error status for a core business rule)
* **Location in Spec:**
  * Section 4.1 "Stake Validation" → "Must not exceed available balance | UI + API | Show/reject as insufficient balance"
  * Section 5.3 `POST /api/place-bet` → "Expected error classes"

* **Description:**
  Insufficient balance is an explicit, testable rejection reason at the API layer, but the "Expected error classes" list does not clearly map it to a status code.
  The candidates are:
  * `422 semantic validation failures (selection/stake/match)` - but insufficient balance is a state/business-rule failure, not strictly a stake **value** validation failure; and "balance" is not listed among `selection/stake/match`.
  * `409` is reserved for "bet already in progress".

* **Impact:**
  * The expected status code for the insufficient-balance case is ambiguous (`422` vs `409` vs `402`), so negative tests cannot assert a specific code.
  * Client integrations cannot reliably distinguish "insufficient balance" from other 422 validation errors without a stable error identifier.

* **Recommendation:**
  Explicitly document the status code and a stable machine-readable error code for insufficient balance (recommended: `422` with an error identifier such as `INSUFFICIENT_BALANCE`, or `402 Payment Required` if a dedicated code is preferred). Extend the 422 description to include "balance".
