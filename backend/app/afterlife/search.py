import httpx2

from app.afterlife.models import SearchResult
from app.afterlife.search_budget import SearchBudget
from app.tracing import traced_tool

SERPAPI_URL = "https://serpapi.com/search.json"
RESULTS = 8


class SearchUnavailableError(Exception):
    pass


class SearchBudgetSpentError(Exception):
    pass


class SerpSearch:
    def __init__(self, client: httpx2.AsyncClient, api_key: str, budget: SearchBudget) -> None:
        self._client = client
        self._api_key = api_key
        self._budget = budget

    @traced_tool("web_search")
    async def results(self, query: str) -> list[SearchResult]:
        if not self._budget.take():
            raise SearchBudgetSpentError(query)
        params = {"engine": "google", "q": query, "num": str(RESULTS), "api_key": self._api_key}
        try:
            response = await self._client.get(SERPAPI_URL, params=params)
            payload = response.raise_for_status().json()
        except (httpx2.HTTPError, ValueError) as error:
            raise SearchUnavailableError(query) from error
        if "error" in payload:
            raise SearchUnavailableError(query)
        items = payload.get("organic_results", [])
        return [SearchResult(link=item["link"], title=item.get("title", "")) for item in items if item.get("link")]
