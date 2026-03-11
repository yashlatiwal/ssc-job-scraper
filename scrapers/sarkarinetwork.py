import requests
from bs4 import BeautifulSoup
import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import find_vacancies, find_qualification, extract_fields_from_detail

URL = "https://sarkarinetwork.com/latest-update/"

def scrape_sarkarinetwork():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    seen = set()

    for row in soup.select("table tr, .post-list li, article, a[href]")[:80]:
        a = row if row.name == "a" else row.select_one("a[href]")
        if not a:
            continue
        title = a.get_text(strip=True)
        link = a.get("href", "")
        if not title or len(title) < 10 or link in seen:
            continue
        if not re.search(r'recruit|vacanc|post|apply|job|exam|notif|form|admit|result', title, re.I):
            continue
        if "comment" in link or re.match(r'^\d+$', title):
            continue
        seen.add(link)

        vac = find_vacancies(title)
        qual = find_qualification(title)
        state = "Central"
        if re.search(r'Haryana|Punjab|Rajasthan|Bihar|UP\b|Assam|Gujarat|Maharashtra|HP\b|J&K|Delhi\b', title, re.I):
            state = "State"

        org = title.split()[0] if title else "Unknown"
        detail = extract_fields_from_detail(link) if link else {}

        jobs.append({
            "org": org,
            "fullOrg": title.split(":")[0].strip() if ":" in title else title[:40],
            "post": title,
            "vacancies": detail.get("vac") or vac,
            "qualification": detail.get("q") or qual,
            "age": detail.get("age", ""),
            "lastDate": detail.get("ld", "TBD"),
            "lastDateFull": detail.get("ld", "TBD"),
            "startDate": "TBD",
            "payLevel": detail.get("pay", ""),
            "category": "Govt",
            "state": state,
            "link": link,
        })

    print(f"  sarkarinetwork: {len(jobs)} listings")
    return jobs
