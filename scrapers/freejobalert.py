import requests
from bs4 import BeautifulSoup
import re, time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import clean, extract_from_tables, merge_with_text, find_vacancies, find_qualification

LISTING_URL = "https://www.freejobalert.com/latest-notifications/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"}

NOISE = re.compile(
    r'(Jobs›|\d+\s*Jobs›?|Result\s*Declared|Answer\s*Key|Admit\s*Card|Exam\s*Date|'
    r'Exam\s*City|Score\s*Card|Cut\s*Off|Syllabus|Interview\s*Results?|DV\s*Candidates|'
    r'All\s*India\s*Govt|State\s*Govt\s*Jobs|Engineering\s*Jobs|Police.Defence|'
    r'Upcoming\s*Notifications|Work\s*From\s*Home|Sports\s*Quota|Ex-Servicemen|'
    r'Examwise|Notification\s*Status|FreeJobAlert)',
    re.I
)

def extract_detail(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(resp.text, "html.parser")
        detail = extract_from_tables(soup)
        text = clean(soup.get_text(separator=" "))
        merged = merge_with_text(detail, text[:3000])
        return {
            "qualification": merged.get("qualification", "Graduation"),
            "age": merged.get("age", ""),
            "lastDate": merged.get("lastDate", "TBD"),
            "payLevel": merged.get("payLevel", ""),
        }
    except:
        return {"qualification": "Graduation", "age": "", "lastDate": "TBD", "payLevel": ""}

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
        if NOISE.search(t):
            continue
        if not re.search(r'recruit|vacanc|apply|notif|form\b', t, re.I):
            continue
        if h.startswith("https://www.freejobalert.com/") and h != LISTING_URL and h not in seen:
            links.append((t, h))
            seen.add(h)

    print(f"  freejobalert: {len(links)} listings")
    jobs = []
    for title, link in links[:30]:
        vac = find_vacancies(title)
        qual = find_qualification(title)
        state = "State" if re.search(r'Haryana|Punjab|Rajasthan|Bihar|\bUP\b|Assam|Gujarat|Maharashtra|\bHP\b|Odisha|Kerala|Tamil|Andhra|Telangana', title, re.I) else "Central"
        d = extract_detail(link)
        time.sleep(0.4)
        jobs.append({
            "org": title.split()[0],
            "fullOrg": title.split(":")[0].strip() if ":" in title else title[:40],
            "post": title,
            "vacancies": vac,
            "qualification": d["qualification"] or qual,
            "age": d["age"],
            "lastDate": d["lastDate"],
            "lastDateFull": d["lastDate"],
            "startDate": "TBD",
            "payLevel": d["payLevel"],
            "category": "Govt",
            "state": state,
            "link": link,
        })

    print(f"  raw count from freejobalert.com: {len(jobs)}")
    return jobs
