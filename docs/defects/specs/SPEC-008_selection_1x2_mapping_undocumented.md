# Spec Defect: SPEC-008 - UI Uses 1 / X / 2 Buttons but Selection Enum Is HOME / DRAW / AWAY (Mapping Undocumented)

* **Severity:** Low (Undocumented mapping between UI controls and API enum)
* **Location in Spec:**
  * Section 2.1 "Match List" → "three selectable odds buttons: 1, X, 2"
  * Section 4.2 "Selection Validation" → "Must be one of HOME, DRAW, AWAY"
  * Section 5.3 `POST /api/place-bet` → `selection: "HOME" | "DRAW" | "AWAY"`
  * `GET /api/matches` → `odds: { home, draw, away }`

* **Description:**
   The UI presents outcomes as `1`, `X`, `2` buttons, while the API enum uses `HOME`, `DRAW`, `AWAY`. The mapping (`1 → HOME`, `X → DRAW`, `2 → AWAY`) **is** documented - but only in the Domain Context prose (`HQA_Take_Home_Task.md`, "Displayed as three buttons per match: `1` (home win), `X` (draw), `2` (away win)"). It is **not** stated in the formal Feature Specification sections where it matters for implementation/testing: Section 2.1 ("Match List"), Section 4.2 ("Selection Validation"), or Section 5.3 (`POST /api/place-bet` response contract).

   Additionally, the "Selection required" rule is marked `UI + API`, while the enum-validity rule is marked `API` only - leaving unclear whether the UI performs any enum-level validation.

* **Impact:**
   * The mapping lives only in the HQA Domain Context, not in the formal spec sections - easy to miss when implementing or writing tests.
   * E2E tests must translate a clicked `1/X/2` button into the expected `selection` enum; that translation is correct per HQA but is not pinned in the API contract, so a future contract change could silently diverge.

* **Recommendation:**
  Document the explicit mapping between UI buttons (`1/X/2`) and the API `selection` enum (`HOME/DRAW/AWAY`), and clarify which validation layer(s) enforce enum validity.
