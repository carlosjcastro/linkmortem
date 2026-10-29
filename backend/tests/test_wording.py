from app.wording import counted, verdict_line


def test_counted_uses_the_singular_for_one():
    assert counted(1, "link") == "1 link"
    assert counted(3, "link") == "3 links"


def test_verdict_line_leaves_out_an_empty_unknown_count():
    assert verdict_line(2, 0) == "2 ghosts"
    assert verdict_line(1, 1) == "1 ghost, 1 could not be confirmed"
