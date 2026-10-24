from app.services.start_sources import normalize_start_payload


def test_normalize_start_payload() -> None:
    assert normalize_start_payload("site") == "site"
    assert normalize_start_payload("health") == "health"
    assert normalize_start_payload(None) == "organic"
    assert normalize_start_payload("Site") == "site"
