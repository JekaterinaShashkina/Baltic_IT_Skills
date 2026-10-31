
from unittest.mock import patch, Mock

from src.meetfrank.fetch_meetfrank import fetch_jobs


def test_incomplete_download():
    fake_response = Mock()
    fake_response.json.return_value = {
        "jobs": [{"id": "TEST-001"}],
        "total": 2,
        "page": 1,
        "pageSize": 100,
        "hasMore": False
    }

    fake_response.raise_for_status.return_value = None

    with patch("src.meetfrank.fetch_meetfrank.requests.get",
            return_value=fake_response):
        try:
            fetch_jobs("estonia")
        except ValueError as error:
            print("EXPECTED ERROR:", error)
        else:
            raise AssertionError(
                "Incomplete download was not detected!"
            )

    print("INCOMPLETE DOWNLOAD TEST PASSED!")

def test_duplicate_jobs():
    first_response = Mock()
    first_response.json.return_value = {
        "jobs": [{"id": "TEST-001"}],
        "total": 2,
        "page": 1,
        "pageSize": 1,
        "hasMore": True
    }

    second_response = Mock()
    second_response.json.return_value = {
        "jobs": [{"id": "TEST-001"}],
        "total": 2,
        "page": 2,
        "pageSize": 1,
        "hasMore": False
    }

    with patch(
        "src.meetfrank.fetch_meetfrank.requests.get",
        side_effect=[first_response, second_response]
    ):
        try:
            fetch_jobs("estonia")
        except ValueError as error:
            assert "duplicate job ID" in str(error)
            print("EXPECTED ERROR:", error)
        else:
            raise AssertionError("Duplicate job was not detected!")

    print("DUPLICATE JOB TEST PASSED!")


def test_successful_pagination():
    first_response = Mock()
    first_response.json.return_value = {
        "jobs": [{"id": "TEST-001"}],
        "total": 2,
        "page": 1,
        "pageSize": 1,
        "hasMore": True
    }

    second_response = Mock()
    second_response.json.return_value = {
        "jobs": [{"id": "TEST-002"}],
        "total": 2,
        "page": 2,
        "pageSize": 1,
        "hasMore": False
    }

    with patch(
        "src.meetfrank.fetch_meetfrank.requests.get",
        side_effect=[first_response, second_response]
    ) as mock_get:
        jobs = fetch_jobs("estonia")

    assert len(jobs) == 2
    assert [job["id"] for job in jobs] == [
        "TEST-001", "TEST-002"
    ]
    assert mock_get.call_count == 2

    print("SUCCESSFUL PAGINATION TEST PASSED!")


if __name__ == "__main__":
    test_incomplete_download()
    test_duplicate_jobs()
    test_successful_pagination()