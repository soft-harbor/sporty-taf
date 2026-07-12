from decimal import ROUND_HALF_UP, Decimal

# Currency precision / rounding rule for monetary outputs (payout, balance).
#
# The spec does NOT define how monetary values are rounded (see
# docs/defects/specs/SPEC-003_payout_rounding_undefined.md). Until that is fixed,
# we assume the de-facto currency standard: two decimal places, half-up rounding
# (ROUND_HALF_UP). This is an application-wide rule shared by the API client,
# steps, and tests, so it lives in the top-level utils package.
MONEY_DECIMALS = 2
_MONEY_QUANTIZE = Decimal("0.01")


def round_money(value: float) -> float:
    """Round a monetary amount to currency precision (2 dp, half-up)."""
    return float(Decimal(str(value)).quantize(_MONEY_QUANTIZE, rounding=ROUND_HALF_UP))
