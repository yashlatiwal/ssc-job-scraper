import requests
from bs4 import BeautifulSoup
import re, time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import find_vacancies, find_qualification, extract_fields_from_detail

URL = "https://govtjobguru.in/"

NOISE = re.compile(
    r'(Jobs›|\d+\s*Jobs›?|Result\s*Declared|Answer\s*Key|Admit\s*Card|Exam\s*Date|'
    r'Exam\s*City|Score\s*Card|Cut\s*Off|Syllabus|A\s*Job\s*Information|'
    r'Active\s*Form|Latest\s*Job\b|Central\s*Job\b|Job\s*Samachar|'
    r'Offline\s*Form\b|Copy\s*Post|Interview\s*Results?|DV\s*Candidates|'
    r'Notification\s*Status|Exam\s*Schedule|Correction\s*Form|Edit\s*Form|BSTC|IGNOU)',
    re.I
)

def clean_title(t):
    # govtjobguru appends: vacancy_count + ORG + qual + date after real title
    t = re.sub(r'\d+[A-Z][A-Za-z].*$', '', t).strip()
    t = re.sub(r'\s*(Bachelor|10\+2|10th|12th|Degree|Diploma|BDS|Various)\s*[\d\w].*$', '', t, flags=re.I).strip()
    t = re.sub(r'\s*\d{1,2}\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*$', '', t, flags=re.I).strip()
    t = re.sub(r'[\s,]+$', '', t).strip()
    return t

def scrape_govtjobguru():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    seen = set()

    for a in soup.select("a[href]")[:120]:
        raw = a.get_text(strip=True)
        title = clean_title(raw)
        link = a.get("href", "")
        if not title or len(title) < 15 or link in seen:
            continue
        if NOISE.search(title):
            continue
        if not re.search(r'recruit|vacanc|apply|notif|form\b', title, re.I):
            continue
        if not link.startswith("http"):
            continue
        seen.add(link)

        vac = find_vacancies(title)   # title only — no detail bleed
        qual = find_qualification(title)
        state = "State" if re.search(r'Haryana|Punjab|Rajasthan|Bihar|UP\b|Assam|Gujarat|Maharashtra|Odisha|Kerala|Tamil|Andhra|Telangana|HP\b', title, re.I) else "Central"
        org = title.split()[0] if title else "Unknown"

        detail = extract_fields_from_detail(link) if link else {}
        if not vac and detail.get("vac"):
            vac = detail["vac"]
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

    print(f"  govtjobguru: {len(jobs)} listings")
    return jobs
