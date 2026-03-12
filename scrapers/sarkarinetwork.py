import requests
from bs4 import BeautifulSoup
import re, time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import find_vacancies, find_qualification, extract_fields_from_detail

URL = "https://sarkarinetwork.com/latest-update/"

NOISE = re.compile(
    r'(Jobs›|\d+\s*Jobs›?|Result\s*Declared|Answer\s*Key|Admit\s*Card|Exam\s*Date|'
    r'Exam\s*City|Score\s*Card|Cut\s*Off|Syllabus|A\s*Job\s*Information|'
    r'Active\s*Form|Latest\s*Job\b|Central\s*Job\b|Job\s*Samachar|'
    r'Offline\s*Form\b|Copy\s*Post|Interview\s*Results?|DV\s*Candidates)',
    re.I
)

def scrape_sarkarinetwork():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    seen = set()

    for a in soup.select("a[href]")[:120]:
        title = a.get_text(strip=True)
        link = a.get("href", "")
        if not title or len(title) < 10 or link in seen:
            continue
        if NOISE.search(title):
            continue
        if not re.search(r'recruit|vacanc|apply|notif|form\b', title, re.I):
            continue
        if not link.startswith("http") or "comment" in link:
            continue
        seen.add(link)

        vac = find_vacancies(title)
        qual = find_qualification(title)
        state = "State" if re.search(r'Haryana|Punjab|Rajasthan|Bihar|UP\b|Assam|Gujarat|Maharashtra|HP\b|J&K|Delhi\b|Odisha|Kerala|Tamil|Andhra|Telangana', title, re.I) else "Central"
        org = title.split()[0] if title else "Unknown"

        detail = extract_fields_from_detail(link) if link else {}
        time.sleep(0.3)

        jobs.append({
            "org": org,
            "fullOrg": title.split(":")[0].strip() if ":" in title else title[:40],
            "post": title,
            "vacancies": vac,
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
