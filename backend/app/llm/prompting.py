import re

FENCE_TAG = re.compile(r"</?[a-z_]+\s*>", re.IGNORECASE)


def as_data(value: str) -> str:
    return FENCE_TAG.sub(" ", value).strip()
