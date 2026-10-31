import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

with open(DATA_DIR / "esco_skill_occupations.json", encoding="utf-8") as f:
    original = json.load(f)

with open(DATA_DIR / "esco_it_occupations.json", encoding="utf-8") as f:
    filtered = json.load(f)


def collect_occupations(data):
    result = {}

    for skill in data.values():
        for relation in ("essential_occupations", "optional_occupations"):
            for occupation in skill.get(relation, []):
                result[occupation["uri"]] = occupation

    return result


all_occupations = collect_occupations(original)
included = collect_occupations(filtered)

excluded = {
    uri: occupation
    for uri, occupation in all_occupations.items()
    if uri not in included
}

print(f"All occupations: {len(all_occupations)}")
print(f"Included: {len(included)}")
print(f"Excluded: {len(excluded)}")

print("\n=== INCLUDED ICT OCCUPATIONS ===")

for occupation in sorted(
    included.values(),
    key=lambda item: item["title"]
):
    print(
        f"{occupation['title']} "
        f"({occupation.get('isco_code', '')})"
    )


# Это только кандидаты для проверки, не окончательный фильтр.
keywords = (
    "ict", "software", "computer", "cloud",
    "data", "network", "cyber", "digital",
    "information technology", "telecommunication",
    "artificial intelligence", "machine learning",
    "iot", "electronics", "microelectronics",
    "system", "web", "application",
    "technology", "programmer"
)

candidates = [
    occupation
    for occupation in excluded.values()
    if any(
        word in occupation["title"].lower()
        for word in keywords
    )
]

print("\n=== EXCLUDED ICT CANDIDATES ===")

for occupation in sorted(
    candidates,
    key=lambda item: item["title"]
):
    print(occupation["title"])

print(f"\nCandidates for review: {len(candidates)}")