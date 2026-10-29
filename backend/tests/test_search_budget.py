from datetime import date

from app.afterlife.search_budget import SearchBudget


def test_budget_runs_out_and_refills_the_next_day():
    days = iter([date(2026, 11, 1), date(2026, 11, 1), date(2026, 11, 1), date(2026, 11, 1), date(2026, 11, 2)])
    budget = SearchBudget(2, lambda: next(days))
    assert [budget.take(), budget.take(), budget.take(), budget.take()] == [True, True, False, True]
