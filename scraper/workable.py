"""Extragerea joburilor Tecknoworks din API-ul public Workable."""

from urllib.parse import urlparse

from . import fetch

WIDGET_URL = (
    "https://apply.workable.com/api/v1/widget/accounts/"
    "tecknoworks?details=true"
)


def parse_workable(data):
    if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
        raise ValueError("Răspuns Workable invalid: lipsește lista jobs")

    jobs = []
    seen = set()

    for row in data["jobs"]:
        if not isinstance(row, dict):
            raise ValueError("Înregistrare Workable invalidă")

        if row.get("country") != "Romania":
            continue

        title = (row.get("title") or "").strip()
        url = (row.get("url") or "").strip()
        parsed = urlparse(url)

        if not title or not (
            parsed.scheme == "https"
            and parsed.hostname == "apply.workable.com"
            and parsed.path.startswith("/j/")
        ):
            raise ValueError("Job românesc fără titlu sau URL Workable valid")

        if url in seen:
            continue
        seen.add(url)

        job = {
            "title": title,
            "url": url,
            "location": [row.get("city") or "România"],
            "source": "apply.workable.com",
        }

        # false nu distinge între hybrid și on-site.
        # Nu atribuim un mod de lucru fără informație explicită.
        if row.get("telecommuting") is True:
            job["workmode"] = "remote"

        jobs.append(job)

    return jobs


def scrape_workable():
    response = fetch.get(
        WIDGET_URL,
        label="workable",
        headers={
            "User-Agent": "TecknoworksJobScraper/1.0",
            "Accept": "application/json",
        },
    )
    response.raise_for_status()
    return parse_workable(response.json())
