import re


def parse_amount(amount: str) -> int:
    cleaned_amount = amount.strip().upper()

    match = re.fullmatch(r"(\d+(?:\.\d+)?)(B|M|K)", cleaned_amount)
    if match:
        value, suffix = float(match.group(1)), match.group(2)
        multipliers = {
            "K": 1_000,
            "M": 1_000_000,
            "B": 1_000_000_000,
        }
        return int(value * multipliers[suffix])

    return int(cleaned_amount)
