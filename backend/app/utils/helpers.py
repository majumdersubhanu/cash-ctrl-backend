from decimal import Decimal


def normalize_amount(value: float) -> Decimal:
    """
    Convert float to Decimal with 2 precision.
    """
    return Decimal(value).quantize(Decimal("0.01"))
