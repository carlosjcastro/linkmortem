class FakeCursor:
    def __init__(self, documents: list[dict]) -> None:
        self.documents = documents

    async def to_list(self, length: int) -> list[dict]:
        return self.documents[:length]


class FakeCollection:
    def __init__(self, matches: list[dict] | None = None) -> None:
        self.documents: dict[str, dict] = {}
        self.matches = matches or []
        self.pipelines: list[list[dict]] = []

    async def find_one(self, query: dict, projection: dict | None = None) -> dict | None:
        found = self.documents.get(query["_id"])
        return {key: value for key, value in found.items() if key != "_id"} if found and projection else found

    async def replace_one(self, query: dict, document: dict, upsert: bool = False) -> None:
        self.documents[query["_id"]] = {"_id": query["_id"], **document}

    async def insert_one(self, document: dict) -> None:
        self.documents[document["_id"]] = document

    async def aggregate(self, pipeline: list[dict]) -> FakeCursor:
        self.pipelines.append(pipeline)
        return FakeCursor(self.matches)
