from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelUsage:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    seconds: float

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


UsageListener = Callable[[ModelUsage], None]
