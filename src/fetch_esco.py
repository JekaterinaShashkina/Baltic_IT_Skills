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


if __name__ == "__main__":
    data = search_esco_skill("Python")

    results = data.get("_embedded", {}).get("results", [])

    print(f"Found {len(results)} results:\n")

    for result in results:
        print("Title:", result.get("title"))
        print("URI:", result.get("uri"))
        print("Search hit:", result.get("searchHit"))
        print("Skill type:", result.get("hasSkillType"))
        print("-" * 50)