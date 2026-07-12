# Spec Defect: SPEC-005 - "Bet Already in Progress" (409) Lifecycle Undefined

* **Severity:** Medium (Untestable concurrency rule)
* **Location in Spec:**
  * Section 5.3 `POST /api/place-bet` → "409 bet already in progress (same user)"
  * Section 2.3 "Place Bet Interaction" → button loading state (`Placing...`)

* **Description:**
  The API defines a `409 bet already in progress (same user)` error, but the spec never defines the lifecycle of an "in progress" bet:
  * When does a bet enter the "in progress" state, and when does it clear?
  * Is placement synchronous (resolves within the single `POST /api/place-bet` request) or asynchronous?
  * What is the concurrency window - how can a second request arrive while the first is still "in progress" if the endpoint is synchronous?

* **Impact:**
  * The condition to deterministically trigger a `409` is unspecified, so an automated concurrency test cannot be written reliably.
  * If a bet stays "in progress" with no timeout documented, the user may be blocked from placing further bets.

* **Recommendation:**
  Document the in-progress lifecycle: what sets and clears the state, whether placement is synchronous, the exact concurrency window that yields `409`, and any timeout or idempotency-key behavior. Consider recommending an idempotency key to make retries safe.
