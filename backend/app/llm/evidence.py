from typing import Annotated

from pydantic import AfterValidator, Field

EVIDENCE_CHARS = 400


def clip(text: str) -> str:
    return text[:EVIDENCE_CHARS]


Evidence = Annotated[str, Field(json_schema_extra={"maxLength": EVIDENCE_CHARS}), AfterValidator(clip)]
