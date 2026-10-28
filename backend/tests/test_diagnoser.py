from app.llm.base import ModelOutputError, ModelUnavailableError
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


class SilentClassifier:
    def __init__(self, error: Exception) -> None:
        self.error = error

    async def classify(self, link, final_url, page):
        raise self.error


async def test_a_missing_model_is_told_apart_from_an_unclear_answer():
    page = Page(200, "https://a.dev/", "text/html", html("Home", LONG_TEXT))
    missing = await Diagnoser(FakeFetcher(page), SilentClassifier(ModelUnavailableError("down"))).diagnose(LINK)
    unclear = await Diagnoser(FakeFetcher(page), SilentClassifier(ModelOutputError("bad"))).diagnose(LINK)
    assert (missing.cause, missing.verdict) == (Cause.MODEL_UNAVAILABLE, Verdict.UNKNOWN)
    assert (unclear.cause, unclear.verdict) == (Cause.UNCLASSIFIED, Verdict.UNKNOWN)


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


async def test_cloudflare_checks_are_restricted_without_the_model():
    classifier = FakeClassifier(PageKind.ALIVE)
    page = Page(200, LINK.url, "text/html", html("One moment, please...", "Please wait while your request is being verified..."))
    result = await Diagnoser(FakeFetcher(page), classifier).diagnose(LINK)
    assert (result.cause, classifier.calls) == (Cause.RESTRICTED, 0)


async def test_github_and_tiktok_bot_answers_are_restricted():
    classifier = FakeClassifier(PageKind.ERROR_PAGE)
    for title, text in [("GitHub Copilot", "You can\u2019t perform that action at this time."), ("", "Please wait...")]:
        result = await Diagnoser(FakeFetcher(Page(200, LINK.url, "text/html", html(title, text))), classifier).diagnose(LINK)
        assert result.cause == Cause.RESTRICTED
    assert classifier.calls == 0
