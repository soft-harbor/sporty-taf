# Spec Defect: SPEC-006 - Filters Defined for UI but No API Contract in GET /api/matches

* **Severity:** Medium (no documented API contract for filters)
* **Location in Spec:**
  * Section 2.6 "Filters" → date filter (single day or inclusive range) and odds filter (inclusive min/max, must reject invalid ranges)
  * Section 5.3 `GET /api/matches` → no query parameters documented

* **Description:**
  Section 2.6 requires date and odds filtering, including rejection of invalid odds ranges "with clear feedback". However, `GET /api/matches` documents no query parameters, request validation, or error response for filtering. It is therefore unclear whether filtering is server-side (API) or purely client-side.

* **Impact:**
  * The API contract for filtering (parameter names, formats, inclusivity, and the error response for an invalid range) is undefined and cannot be tested at the API layer.
  * If filtering is client-side only, invalid-range rejection and its error handling are unspecified.
  * Inclusive-boundary behavior (dates and odds) is stated for the UI but not tied to any concrete contract.

* **Recommendation:**
  Decide and document the filtering layer. If server-side, define the query parameters (e.g. `dateFrom`, `dateTo`, `oddsMin`, `oddsMax`), their formats, inclusive semantics, and the error status/body returned for an invalid range (e.g. `oddsMin > oddsMax`). If client-side only, state that explicitly and define the validation feedback behavior.
