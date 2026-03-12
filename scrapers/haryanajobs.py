import requests
from bs4 import BeautifulSoup
import re, time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import find_vacancies, find_qualification, extract_fields_from_detail

URLS = [
    "https://haryanajobs.in/category/latest-jobs/",
    "https://haryanajobs.in/",
]

NOISE = re.compile(
    r'(Result\s*Declared|Answer\s*Key|Admit\s*Card|Exam\s*Date|Exam\s*City|'
    r'Score\s*Card|Cut\s*Off|Interview\s*Results?|DV\s*Candidates|Syllabus)',
    re.I
)

def scrape_haryanajobs():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
    }
    jobs = []
    seen = set()

    for url in URLS:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            print(f"  haryanajobs → HTTP {resp.status_code}")
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")

            for article in soup.select("article.post, .post, h2.entry-title, h3.entry-title")[:50]:
                a = article.select_one("a[href]") if article.name != "a" else article
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
                seen.add(link)

                vac = find_vacancies(title)
                qual = find_qualification(title)
                state = "Central" if re.search(r'\bSSC\b|\bUPSC\b|\bRRB\b|\bRBI\b|\bSBI\b|\bNDA\b|\bCDS\b|\bNDA\b', title, re.I) else "State"
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
        except Exception as e:
            print(f"  haryanajobs error: {e}")

    print(f"  raw count from haryanajobs.in: {len(jobs)}")
    return jobs
