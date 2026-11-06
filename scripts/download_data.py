"""
Download trusted health-topic summaries from MedlinePlus into data/.

MedlinePlus is run by the US National Library of Medicine (NLM).
We use its official free search service, so no scraping and no API key.

Run it (from the project folder):  python scripts/download_data.py
"""

import html
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
API_URL = "https://wsearch.nlm.nih.gov/ws/query"

# Topics that often appear in medical reports. Add more any time.
TOPICS = [
    "Diabetes",
    "High Blood Pressure",
    "Anemia",
    "Hypothyroidism",
    "Hyperthyroidism",
    "Cholesterol",
    "Blood Count Tests",
    "Liver Diseases",
    "Kidney Tests",
    "Vitamin D",
]

# MedlinePlus sends this table with its cells already stuck together, so row
# breaks can't be worked out from the text. The values below are unchanged.
FLAT_BLOOD_PRESSURE_TABLE = (
    "Blood Pressure CategorySystolic Blood PressureDiastolic Blood Pressure"
    "NormalLess than 120andLess than 80"
    "Elevated120 - 129andLess than 80"
    "High Blood Pressure Stage 1130 - 139or80 - 89"
    "High Blood Pressure Stage 2140 or higheror90 or higher"
    "Hypertensive Crisis (dangerously high blood pressure - seek medical care right away)"
    "Higher than 180andHigher than 120"
)
BLOOD_PRESSURE_TABLE = """Blood pressure categories:
- Normal: systolic less than 120 and diastolic less than 80
- Elevated: systolic 120 - 129 and diastolic less than 80
- High Blood Pressure Stage 1: systolic 130 - 139 or diastolic 80 - 89
- High Blood Pressure Stage 2: systolic 140 or higher or diastolic 90 or higher
- Hypertensive Crisis (dangerously high blood pressure - seek medical care right away): systolic higher than 180 and diastolic higher than 120"""


def html_to_text(raw: str) -> str:
    """Turn the HTML summary into plain text with line breaks."""
    # Headings arrive as bare text right before <p>, so <p> needs a break too.
    text = re.sub(r"</?p\b[^>]*>|<br\s*/?>|</h\d>|</?[uo]l\b[^>]*>", "\n\n", raw)
    text = re.sub(r"<li>", "\n- ", text)
    text = re.sub(r"<[^>]+>", "", text)          # remove remaining tags
    text = html.unescape(text)                   # &amp; -> &
    text = text.replace(FLAT_BLOOD_PRESSURE_TABLE, BLOOD_PRESSURE_TABLE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_topic(topic: str) -> dict | None:
    """Search MedlinePlus and return the best matching topic page."""
    query = urllib.parse.urlencode({"db": "healthTopics", "term": topic, "retmax": 10})
    request = urllib.request.Request(
        f"{API_URL}?{query}", headers={"User-Agent": "medical-chatbot-student-project"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())

    results = []
    for doc in root.iter("document"):
        fields = {c.get("name"): c.text or "" for c in doc.findall("content")}
        title = html_to_text(fields.get("title", ""))
        summary = fields.get("FullSummary", "")
        if title and summary:
            results.append({"title": title, "url": doc.get("url"), "summary": html_to_text(summary)})

    # Prefer the exact topic name, otherwise take the top result.
    for result in results:
        if result["title"].lower() == topic.lower():
            return result
    return results[0] if results else None


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    for topic in TOPICS:
        result = fetch_topic(topic)
        if result is None:
            print(f"  skipped: {topic} (no result)")
            continue
        file_name = re.sub(r"[^a-z0-9]+", "-", result["title"].lower()).strip("-") + ".txt"
        content = (
            f"{result['title']}\n"
            f"Source: MedlinePlus, U.S. National Library of Medicine\n"
            f"URL: {result['url']}\n\n"
            f"{result['summary']}\n"
        )
        (DATA_DIR / file_name).write_text(content, encoding="utf-8")
        print(f"  saved: data/{file_name} ({len(content)} characters)")
        time.sleep(1)  # be polite to the free service
    print("Done.")


if __name__ == "__main__":
    main()