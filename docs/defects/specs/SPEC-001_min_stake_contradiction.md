# Spec Defect: SPEC-001 - Contradictory Minimum Stake Value (€1.00 vs €1.01)

* **Severity:** High (Contradictory acceptance criteria)
* **Location in Spec:**
  * Section 3 "Business Rules" → `Stake min (per bet) = €1.00`
  * Section 4.1 "Stake Validation" → `Stake | Minimum €1.01 (positive values)`
  * Section 4.4 "UI Error Messaging" → `Minimum stake is €1.00`

* **Description:**
  The specification defines the minimum allowed stake inconsistently. The Business Rules table and the UI error copy both state the minimum is **€1.00**, while the Stake Validation table (4.1) states the minimum is **€1.01**.

  This makes the exact boundary undefined: it is unclear whether a stake of exactly **€1.00** should be **accepted** (inclusive minimum) or **rejected** (exclusive minimum / minimum is 1.01).

* **Likely Root Cause (Assessment):**
  Based on the logic and intent of the feature, the correct minimum is **€1.00**. Two of the three sources (Business Rules and the user-facing error copy) agree on €1.00, and €1.00 is the natural, round currency boundary for a "minimum stake". The **€1.01 in section 4.1 is almost certainly a typo**, not an intentional exclusive boundary.

  This is called out explicitly because, despite being a probable typo, it is **dangerous**: a developer implementing strictly against section 4.1 would build `stake >= 1.01` (rejecting a valid €1.00 bet), and the misleading UI copy ("Minimum stake is €1.00") would make the resulting defect hard to spot.

* **Impact:**
  * Boundary tests at €1.00 cannot be authored deterministically.
  * UI and API layers may implement different boundaries, producing inconsistent validation between client and server.
  * Given the fact that €1.00 could be common (e.g., for small wagers), the ambiguity could lead to a revenue loss and customer frustration.
  * Displayed error copy ("Minimum stake is €1.00") would additionaly confuse users who attempt to place a €1.00 bet (in case of a defect in the implementation).

* **Recommendation:**
  Treat **€1.00 as the inclusive minimum** (`stake >= 1.00`), matching the Business Rules and the user-facing error copy, and correct the **€1.01 typo in section 4.1** so all three sections agree. Until the spec owner confirms, document this assumption as the basis for implementation and tests.
