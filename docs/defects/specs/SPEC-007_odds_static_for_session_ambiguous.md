# Spec Defect: SPEC-007 - "Odds Static for Session" Is Ambiguous

* **Severity:** Low (Ambiguous term affecting price-consistency testing)
* **Location in Spec:**
  * Section 3 "Business Rules" → "Odds behavior | Static for session"
  * Section 2.4 "Success Receipt" → "Odds at placement"
  * Domain Context (HQA) → "Bet Receipt ... All values should be consistent with what was shown before placement."

* **Description:**
  "Static for session" is not defined. It is unclear what "session" means:
  * a browser/UI session,
  * a user API session (per `x-user-id`),
  * a server process/deployment window, or
  * the lifetime between balance resets.

  It is also unclear how "odds at placement" are guaranteed to match the odds shown in the match list if odds could ever change between page load and placement.

* **Impact:**
  * Tests asserting price consistency (list odds == receipt "odds at placement") have no defined stability window to rely on.
  * Ambiguity risks a mismatch between the potential payout shown before placement and the receipt, contradicting the domain requirement of value consistency.

* **Recommendation:**
  Define "session" precisely and state the odds stability guarantee, e.g. "odds are fixed per match for the lifetime of the server deployment and never change within a user session; the odds used at placement are the odds returned by `GET /api/matches`."
