import requests

ESCO_API_URL = "https://ec.europa.eu/esco/api/search"


def search_esco_skill(skill_name):
    params = {
        "text": skill_name,
        "language": "en",
        "type": "skill",
        "limit": 10,
        "selectedVersion": "v1.2.0"
    }

    response = requests.get(
        ESCO_API_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "application/json" not in content_type.lower():
        raise ValueError(
            f"ESCO API returned unexpected content: "
            f"HTTP {response.status_code}, "
            f"Content-Type: {content_type}"
        )

    return response.json()


def get_esco_skill_details(esco_uri):
    url = "https://ec.europa.eu/esco/api/resource/skill"

    params = {
        "uri": esco_uri,
        "language": "en",
        "selectedVersion": "v1.2.0"
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    if "application/json" not in content_type.lower():
        raise ValueError(
            f"ESCO API returned unexpected content: "
            f"HTTP {response.status_code}, "
            f"Content-Type: {content_type}"
        )

    return response.json()




if __name__ == "__main__":
    uri = "http://data.europa.eu/esco/skill/21d2f96d-35f7-4e3f-9745-c533d2dd6e97"

    details = get_esco_skill_details(uri)

    print("Preferred label:")
    print(details.get("preferredLabel", {}).get("en"))

    print("\nAlternative labels:")
    print(details.get("alternativeLabel", {}).get("en", []))

    print("\nDescription:")
    print(details.get("description", {}).get("en"))

