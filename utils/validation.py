"""Small parsing helpers used by the GUI."""


def parse_integer(text: str, field_name: str) -> int:
    try:
        return int(text.strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a whole number.") from exc
