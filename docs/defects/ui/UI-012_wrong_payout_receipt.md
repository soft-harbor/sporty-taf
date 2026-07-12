# Bug ID: UI-012 - Bet Receipt Shows Incorrect "Potential Payout" (Always stake × 2, Hardcoded; Ignores Actual Odds and API Payout)

* **Severity:** High
* **Reproduction Steps:**
  1. Place a bet whose odds are **not** `2.0` (e.g. odds `2.45`, stake `10`).
  2. Open the success receipt and read the "Potential Payout" (or payout) value.
  3. Compare it with `stake × actual odds` and with the `payout` field returned by `POST /api/place-bet`.
* **Expected Result:**
  Per Spec Section 2.4 ("Success Receipt") all values must be consistent with what was shown before placement. The receipt should **display the server-computed `payout`** (or recompute it as `stake × odds` with the real odds), matching both the bet slip's computed value and the `payout` from `POST /api/place-bet` (see [SPEC-003](../specs/SPEC-003_payout_rounding_undefined.md)).
* **Actual Result:**
  The receipt's "Potential Payout" is **always `stake × 2`**, regardless of the actual odds - it hardcodes a coefficient of `2` instead of using the real odds or the `payout` returned by the API. Note the contrast: the **bet slip** computes the stake/payout correctly, and **`/place-bet` returns the correct `payout`** - only the **receipt display** is wrong (it recomputes with a hardcoded multiplier rather than showing the API value).
* **Business Impact:**
  Users see the wrong potential winnings on the receipt. In a licensed market, the payout on a bet confirmation must match the placed bet. Together with [UI-010](../ui/UI-010_receipt_missing_info.md) (missing info, swapped teams), the receipt cannot be relied on as proof of placement.
* **Evidence:**
  Receipt screenshot - "Potential Payout" equals `stake × 2` independent of odds; compare with the correct `payout` in the `/place-bet` response. See also [SPEC-003](../specs/SPEC-003_payout_rounding_undefined.md) (payout consistency) and [API-006](../api/API-006_place-bet_currency_usd.md) (other wrong financial figures on responses).
![UI-012_wrong_payout_receipt.png](attachments/UI-012_wrong_payout_receipt.png)
