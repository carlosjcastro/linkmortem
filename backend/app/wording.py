def counted(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def verdict_line(ghosts: int, unknown: int) -> str:
    line = counted(ghosts, "ghost")
    return f"{line}, {unknown} could not be confirmed" if unknown else line
