import requests
from bs4 import BeautifulSoup
import re, time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import find_vacancies, find_qualification, extract_fields_from_detail, infer_pay_from_text

URL = "https://sarkarinetwork.com/latest-update/"

NOISE = re.compile(
    r'(Jobs[›\s]|\d+\s*Jobs\b|Result\s*Declared|Answer\s*Key|Admit\s*Card|'
    r'Exam\s*Date|Exam\s*City|Score\s*Card|Cut\s*Off|Syllabus|'
    r'Correction\s*Form|Edit\s*Form|TEE\s*.*Exam|BSTC|IGNOU|'
    r'Interview\s*Results?|DV\s*Candidates|Online\s*Form\s*\d{4}$)',
    re.I
)

def scrape_sarkarinetwork():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    seen = set()

    for row in soup.select("table tr, .post-list li, article, a[href]")[:120]:
        a = row if row.name == "a" else row.select_one("a[href]")
        if not a:
            continue
        title = a.get_text(strip=True)
        link = a.get("href", "")
        if not title or len(title) < 10 or link in seen:
            continue
        if NOISE.search(title):
            continue
        # Must mention vacancies or recruitment — not just a form
        if not re.search(r'recruit|vacanc|notif|vacancy', title, re.I):
            continue
        if "comment" in link:
            continue
        seen.add(link)

        vac = find_vacancies(title)
        qual = find_qualification(title)
        state = "State" if re.search(r'Haryana|Punjab|Rajasthan|Bihar|\bUP\b|Assam|Gujarat|Maharashtra|\bHP\b|J&K|Delhi\b', title, re.I) else "Central"
        org = title.split()[0]

        detail = extract_fields_from_detail(link) if link else {}
        pay = detail.get("pay") or infer_pay_from_text(title)

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
            "payLevel": pay or "",
            "category": "Govt",
            "state": state,
            "link": link,
        })
        time.sleep(0.3)

    print(f"  sarkarinetwork: {len(jobs)} listings")
    return jobs
