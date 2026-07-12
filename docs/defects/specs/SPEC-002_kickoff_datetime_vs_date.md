# Spec Defect: SPEC-002 - Kickoff "date/time" Required by UI but API Only Returns a Date

* **Severity:** Medium (UI requirement cannot be satisfied by the documented API contract)
* **Location in Spec:**
  * Section 2.1 "Match List" → "kickoff **date/time** label"
  * Section 5.3 `GET /api/matches` → `kickoffDate: string (YYYY-MM-DD)`

* **Description:**
  The Match List functional requirement states each match must show a kickoff **date/time** label. However, the documented `GET /api/matches` response only exposes `kickoffDate` as a date in `YYYY-MM-DD` format, with no time component and no timezone.

* **Impact:**
  * The UI cannot display a kickoff **time** using the documented contract.
  * No timezone is specified, so any time rendering would be ambiguous across regions.
  * Tests asserting a kickoff time in the UI have no backing data field to validate against.

* **Recommendation:**
  Reconcile the contract with the UI requirement. Either:
  * **Option A:** Extend the API to return a full timestamp (e.g. `kickoffTime: string` with timezone / UTC) - preferable, or
  * **Option B:** Change the UI requirement to "kickoff date label" only.

  Whichever is chosen, the field name, format, and timezone convention must be stated explicitly.
