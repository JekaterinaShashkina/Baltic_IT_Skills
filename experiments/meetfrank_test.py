import requests
import sys
import json

sys.stdout.reconfigure(encoding="utf-8")


URL = "https://api.meetfrank.com/ai/jobs"

countries = ["estonia", "latvia", "lithuania"]

for country in countries:
    params = {
        "country": country,
        "speciality": "software engineering",
        "pageSize": 100
    }



    response = requests.get(URL, params=params)
    response.raise_for_status()

    data = response.json()

    filename = f"meetfrank_{country}_jobs.json"

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"{country.capitalize()}: {len(data.get('jobs', []))} jobs")
    print(f"Saved: {filename}")