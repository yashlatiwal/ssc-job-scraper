import requests
from bs4 import BeautifulSoup
import re, time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import clean, extract_from_tables, merge_with_text

LISTING_URL = "https://www.freejobalert.com/latest-notifications/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"}

# Navigation/category links to skip
NOISE = re.compile(
    r'^(Apprentices\d*\s*Jobs|Professors\d*\s*Jobs|Teachers\d*\s*Jobs|Clerks\d*\s*Jobs|'
    r'Doctors\d*\s*Jobs|Security\s*Officers\d*\s*Jobs|Engineers\d*\s*Jobs|'
    r'All\s*India\s*Govt|State\s*Govt\s*Jobs|Engineering\s*Jobs|Police/Defence|'
    r'Upcoming\s*Notifications|Work\s*From\s*Home|Sports\s*Quota|Ex-Servicemen|'
    r'Examwise|Notification\s*Status|FreeJobAlert|Anganwadi\s*Recruitment)\b',
    re.I
)

def extract_detail(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        detail = extract_from_tables(soup)
        text = clean(soup.get_text(separator=" "))
        merged = merge_with_text(detail, text)
        return {
            "vacancies": merged.get("vacancies", 0),
            "qualification": merged.get("qualification", "Graduation"),
            "age": merged.get("age", ""),
            "lastDate": merged.get("lastDate", "TBD"),
            "lastDateFull": merged.get("lastDate", "TBD"),
            "payLevel": merged.get("payLevel", ""),
        }
    except Exception as e:
        print(f"    ⚠️ {e}")
        return {"vacancies": 0, "qualification": "Graduation", "age": "", "lastDate": "TBD", "lastDateFull": "TBD", "payLevel": ""}

def scrape_freejobalert():
    resp = requests.get(LISTING_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    seen = set()
    links = []

    for a in soup.select("a[href]"):
        t = a.get_text(strip=True)
        h = a.get("href", "")
        if not t or len(t) < 15:
            continue
        if NOISE.match(t):
            continue
        if not re.search(r'recruit|vacanc|post|apply|notif|job|exam|form|admit|result', t, re.I):
            continue
        if h.startswith("https://www.freejobalert.com/") and h != LISTING_URL and h not in seen:
            links.append((t, h))
            seen.add(h)

    print(f"  freejobalert: {len(links)} listings")
    jobs = []
    for title, link in links[:30]:
        print(f"    → {title[:70]}")
        d = extract_detail(link)
        time.sleep(0.5)
        vt = re.search(r'(\d{2,6})\s*(Posts?|Vacancy|Vacancies)', title, re.I)
        state = "State" if re.search(r'Haryana|Punjab|Rajasthan|Bihar|\bUP\b|Assam|Gujarat|Maharashtra|\bHP\b|Odisha|Kerala|Tamil|Andhra|Telangana', title, re.I) else "Central"
        jobs.append({
            "org": title.split()[0],
            "fullOrg": title.split(":")[0].strip() if ":" in title else title.split()[0],
            "post": title,
            "vacancies": d["vacancies"] or (int(vt.group(1)) if vt else 0),
            "qualification": d["qualification"],
            "age": d["age"],
            "lastDate": d["lastDate"],
            "lastDateFull": d["lastDateFull"],
            "startDate": "TBD",
            "payLevel": d["payLevel"],
            "category": "Govt",
            "state": state,
            "link": link,
            "source": "freejobalert.com",
        })
    print(f"  raw count from freejobalert.com: {len(jobs)}")
    return jobs
