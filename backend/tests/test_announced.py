from app.afterlife.announced import announced_move

ORIGINAL = "https://airbnb.io/enzyme/index.html"


def test_reads_the_new_address_a_dead_page_announced():
    move = announced_move(ORIGINAL, "Airbnb.io Mobile Open Source Enzyme has moved. Redirecting now to enzymejs.github.io ... Careers")
    assert move.candidates == ["https://enzymejs.github.io/enzyme/index.html", "https://enzymejs.github.io"]
    assert move.quote == "Airbnb.io Mobile Open Source Enzyme has moved. Redirecting now to enzymejs.github.io"


def test_keeps_a_full_destination_as_written():
    move = announced_move(ORIGINAL, "This project has moved permanently to https://new.dev/docs/enzyme.")
    assert move.candidates == ["https://new.dev/docs/enzyme"]


def test_ignores_moves_within_the_same_site_or_to_an_archive():
    assert announced_move(ORIGINAL, "Moved to airbnb.io/other").candidates == []
    assert announced_move(ORIGINAL, "Moved to web.archive.org/web/2019").candidates == []
    assert announced_move(ORIGINAL, "Nothing moved here.").candidates == []
