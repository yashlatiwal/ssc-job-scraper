import requests
from bs4 import BeautifulSoup
import re
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import find_vacancies, find_qualification

URL = "https://sarkarinetwork.com/latest-update/"

NOISE = re.compile(
    r'(Jobs›|Jobs\s*›|\d+\s*Jobs|Result\s*Declared|Answer\s*Key|'
    r'Admit\s*Card|Exam\s*Date|Exam\s*City|Score\s*Card|Cut\s*Off|'
    r'A\s*Job\s*Information|Active\s*Form|Latest\s*Job\b|Central\s*Job\b|'
    r'Job\s*Samachar|Offline\s*Form\b|Exam\s*Syllabus|Copy\s*Post|'
    r'Interview\s*Results?|DV\s*Candidates)',
    re.I
)

def scrape_sarkarinetwork():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    seen = set()

    for row in soup.select("table tr, .post-list li, article, a[href]")[:100]:
        a = row if row.name == "a" else row.select_one("a[href]")
        if not a:
            continue
        title = a.get_text(strip=True)
        link = a.get("href", "")
        if not title or len(title) < 10 or link in seen:
            continue
        if NOISE.search(title):
            continue
        if not re.search(r'recruit|vacanc|apply|notif|form\b', title, re.I):
            continue
        if "comment" in link:
            continue
        seen.add(link)

        vac = find_vacancies(title)
        qual = find_qualification(title)
        state = "Central"
        if re.search(r'Haryana|Punjab|Rajasthan|Bihar|UP\b|Assam|Gujarat|Maharashtra|HP\b|J&K|Delhi\b', title, re.I):
            state = "State"

        jobs.append({
            "org": title.split()[0] if title else "Unknown",
            "fullOrg": title.split(":")[0].strip() if ":" in title else title[:40],
            "post": title,
            "vacancies": vac,
            "qualification": qual,
            "age": "",
            "lastDate": "TBD",
            "lastDateFull": "TBD",
            "startDate": "TBD",
            "payLevel": "",
            "category": "Govt",
            "state": state,
            "link": link,
        })

    print(f"  sarkarinetwork: {len(jobs)} listings")
    return jobs
