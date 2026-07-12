# Spec Defect: SPEC-003 - Payout Precision / Rounding Rule Undefined

* **Severity:** Medium (Financial calculation without a defined rounding rule)
* **Location in Spec:**
  * Section 2.4 "Success Receipt" → "Potential payout"
  * Section 5.3 `POST /api/place-bet` → `payout: number`
  * Domain Context (HQA) → "Payout ... Calculated as `stake × odds`"

* **Description:**
  The spec defines payout as `stake × odds` but never states how the result is rounded or how many decimal places are retained. Because `stake` allows up to 2 decimal places and `odds` are decimals (e.g. 2.45), the raw product frequently yields more than 2 decimal places (e.g. `10.01 × 2.45 = 24.5245`).

* **Impact:**
  * Undefined rounding for a monetary value: UI, receipt, and API could each round differently (round half-up, half-even, truncate), causing mismatches.
  * Tests cannot assert an exact `payout` value without an agreed rounding rule.
  * Potential customer-facing discrepancy between the "potential payout" shown before placement and the value on the receipt.

* **Recommendation:**
  Specify an explicit rounding rule for all monetary outputs (`payout`, `balance`), e.g. "round to 2 decimal places using half-up rounding, currency EUR". UI, receipt, and API must all apply the same rule so pre-placement and post-placement values match.
