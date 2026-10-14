import requests
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://ec.europa.eu/esco/api/search"

skills = [
    "Python",
    "Java",
    "React",
    "Docker",
    "Kubernetes",
    "CI and CD",
    "Full-Stack Development"
]


for skill in skills:
    params = {
        "text": skill,
        "language": "en",
        "type": "skill",
        "limit": 10,
        "selectedVersion": "v1.2.0"
    }


    response = requests.get(URL, params=params)
    response.raise_for_status()

    data = response.json()

    filename = f"esco_{skill}.json"

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )



    print(f"{skill}: {data.get('total', 0)} results")
    print(f"Saved: {filename}")