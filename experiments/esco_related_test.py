import requests
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

URL = "https://ec.europa.eu/esco/api/resource/skill"

java_uri = "http://data.europa.eu/esco/skill/19a8293b-8e95-4de3-983f-77484079c389"

params = {
    "uri": java_uri,
    "language": "en",
    "selectedVersion": "v1.2.0"
}

response = requests.get(URL, params=params)

print("Status:", response.status_code)
print("Response:", response.text)

response.raise_for_status()

data = response.json()

with open("esco_java_skill.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Saved: esco_java_skill.json")