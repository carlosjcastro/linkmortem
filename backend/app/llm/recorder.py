import asyncio
from pathlib import Path

from pydantic import BaseModel

from app.llm.base import StructuredModel
from app.llm.cases import EvalCase, append_case, case_id


class RecordingModel:
    def __init__(self, inner: StructuredModel, path: Path) -> None:
        self._inner = inner
        self._path = path

    @property
    def name(self) -> str:
        return self._inner.name

    async def generate[Schema: BaseModel](self, system: str, prompt: str, schema: type[Schema]) -> Schema:
        result = await self._inner.generate(system, prompt, schema)
        case = EvalCase(
            id=case_id(system, prompt),
            task=schema.__name__,
            system=system,
            prompt=prompt,
            captured_model=self._inner.name,
            captured_answer=result.model_dump(mode="json"),
        )
        await asyncio.to_thread(append_case, self._path, case)
        return result
