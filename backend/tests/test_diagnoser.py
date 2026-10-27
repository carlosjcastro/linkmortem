from app.scan.diagnoser import Diagnoser
from app.scan.fetcher import Page
from app.scan.models import Cause, Link, PageClassification, PageKind, Verdict

LINK = Link(url="https://a.dev/docs/v1", source="https://site.dev", text="Install guide")
LONG_TEXT = "Installation steps for the tool. " * 40


class FakeFetcher:
    def __init__(self, page: Page) -> None:
        self.page = page

    async def fetch(self, url: str) -> Page:
        return self.page


class FakeClassifier:
    def __init__(self, kind: PageKind) -> None:
        self.kind = kind
        self.calls = 0

    async def classify(self, link, final_url, page):
        self.calls += 1
        return PageClassification(kind=self.kind, evidence="Welcome to our home page")


def html(title: str, text: str) -> str:
    return f"<title>{title}</title><p>{text}</p>"


async def test_dead_status_skips_the_model():
    classifier = FakeClassifier(PageKind.ALIVE)
    result = await Diagnoser(FakeFetcher(Page(404, LINK.url)), classifier).diagnose(LINK)
    assert (result.cause, result.verdict, classifier.calls) == (Cause.NOT_FOUND, Verdict.GHOST, 0)


async def test_parked_domains_are_caught_by_code():
    page = Page(200, LINK.url, "text/html", html("Sale", "This domain is for sale"))
    result = await Diagnoser(FakeFetcher(page), FakeClassifier(PageKind.ALIVE)).diagnose(LINK)
    assert result.cause == Cause.PARKED_DOMAIN and "for sale" in result.evidence


async def test_healthy_pages_skip_the_model():
    classifier = FakeClassifier(PageKind.ERROR_PAGE)
    page = Page(200, LINK.url, "text/html", html("Install", LONG_TEXT))
    result = await Diagnoser(FakeFetcher(page), classifier).diagnose(LINK)
    assert result.verdict == Verdict.ALIVE and classifier.calls == 0


async def test_suspicious_pages_are_judged_by_the_model():
    page = Page(200, "https://a.dev/", "text/html", html("Home", LONG_TEXT))
    result = await Diagnoser(FakeFetcher(page), FakeClassifier(PageKind.UNRELATED)).diagnose(LINK)
    assert result.cause == Cause.UNRELATED_REDIRECT and result.verdict == Verdict.GHOST


async def test_pages_without_readable_text_are_never_ghosts():
    classifier = FakeClassifier(PageKind.ERROR_PAGE)
    page = Page(200, "https://www.youtube.com/watch?v=x", "text/html", "<title>Video</title><script>app()</script>")
    result = await Diagnoser(FakeFetcher(page), classifier).diagnose(LINK)
    assert (result.cause, result.verdict, classifier.calls) == (Cause.UNREADABLE, Verdict.ALIVE, 0)


async def test_browser_gates_are_restricted_without_the_model():
    classifier = FakeClassifier(PageKind.ERROR_PAGE)
    page = Page(200, LINK.url, "text/html", html("Docs", "Ya no se admite esta versión. Actualiza a un navegador admitido."))
    result = await Diagnoser(FakeFetcher(page), classifier).diagnose(LINK)
    assert (result.cause, result.verdict, classifier.calls) == (Cause.RESTRICTED, Verdict.UNKNOWN, 0)
