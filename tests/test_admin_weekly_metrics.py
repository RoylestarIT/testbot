from app.services.admin_weekly_metrics import _pct


def test_pct_format() -> None:
    assert _pct(3, 10) == "30%"
    assert _pct(0, 0) == "—"
