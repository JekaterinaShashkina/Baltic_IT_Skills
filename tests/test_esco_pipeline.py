
from src.esco import match_esco


def test_esco_exact_match(monkeypatch):
    # Simulate one unprocessed MeetFrank skill
    monkeypatch.setattr(
        match_esco,
        "get_skills",
        lambda limit=20: ["Python"]
    )

    # Simulate an ESCO API search response
    monkeypatch.setattr(
        match_esco,
        "search_esco_skill",
        lambda skill: {
            "_embedded": {
                "results": [
                    {"uri": "http://example.com/esco/python"}
                ]
            }
        }
    )

    # Simulate ESCO skill details
    monkeypatch.setattr(
        match_esco,
        "get_esco_skill_details",
        lambda uri: {
            "preferredLabel": {
                "en": "Python"
            },
            "alternativeLabel": {
                "en": []
            }
        }
    )

    saved_mappings = []
    saved_checks = []

    # Capture database writes without modifying SQLite
    monkeypatch.setattr(
        match_esco,
        "save_esco_mapping",
        lambda *args, **kwargs: saved_mappings.append((args, kwargs))
    )

    monkeypatch.setattr(
        match_esco,
        "save_esco_check",
        lambda skill, status: saved_checks.append((skill, status))
    )

    # Skip the delay between API requests
    monkeypatch.setattr(match_esco.time, "sleep", lambda seconds: None)

    stats = match_esco.check_esco_matches(limit=20)

    assert stats == {
        "checked": 1,
        "matched": 1,
        "no_match": 0,
        "failed": 0
    }

    assert len(saved_mappings) == 1
    assert saved_checks == [("Python", "exact")]
