"""Small independent rational oracle; no AST, Decimal context or production imports."""

import re
from fractions import Fraction


def rational(text: str) -> Fraction:
    if not isinstance(text, str) or len(text) > 250 or not re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        raise ValueError("Expected bounded decimal text, not float or scientific notation")
    return Fraction(text)


def quantize(value: Fraction, scale: int, mode: str) -> str:
    if not isinstance(scale, int) or isinstance(scale, bool) or not 0 <= scale <= 12:
        raise ValueError("Reference scale must be between 0 and 12")
    modes = {"ROUND_HALF_UP", "ROUND_HALF_EVEN", "ROUND_UP", "ROUND_DOWN"}
    if mode not in modes:
        raise ValueError("Unsupported reference rounding")
    magnitude = abs(value) * 10**scale
    lower = magnitude.numerator // magnitude.denominator
    distance = magnitude - lower
    if mode == "ROUND_DOWN":
        integer = lower
    elif mode == "ROUND_UP":
        integer = lower + (distance > 0)
    elif distance < Fraction(1, 2):
        integer = lower
    elif distance > Fraction(1, 2) or mode == "ROUND_HALF_UP":
        integer = lower + 1
    else:
        integer = lower if lower % 2 == 0 else lower + 1
    digits = str(integer).zfill(scale + 1)
    result = digits if scale == 0 else (digits[:-scale] + "." + digits[-scale:]).rstrip("0").rstrip(".")
    return ("-" if value < 0 and integer else "") + result


def price(*, quantity="1", rate="100", minimum=None, surcharge="0", scale=2, mode="ROUND_HALF_UP"):
    """surcharge is an explicit fraction (0.05=5%), applied after the minimum."""
    subtotal = rational(quantity) * rational(rate)
    if minimum is not None:
        subtotal = max(subtotal, rational(minimum))
    return quantize(subtotal * (1 + rational(surcharge)), scale, mode)
