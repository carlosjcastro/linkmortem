from app.scan.link_index import LinkIndex


def test_keeps_the_first_source_and_adds_the_others_once():
    index = LinkIndex()
    assert index.add("https://a.dev", "README.md", "A") is True
    assert index.add("https://a.dev", "docs/guide.md", "again") is False
    assert index.add("https://a.dev", "docs/guide.md", "twice") is False
    assert index.add("https://a.dev", "README.md", "same file") is False
    [link] = index.links()
    assert (link.source, link.text, link.other_sources) == ("README.md", "A", ["docs/guide.md"])
