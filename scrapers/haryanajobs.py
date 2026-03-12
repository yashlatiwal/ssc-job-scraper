import requests
from bs4 import BeautifulSoup
import re, time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import find_vacancies, find_qualification, extract_fields_from_detail, infer_pay_from_text

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

            # Try multiple selectors — site structure varies
            candidates = (
                soup.select("article a[href]") or
                soup.select("h2.entry-title a, h3.entry-title a") or
                soup.select(".post-title a, .entry-title a") or
                soup.select("a[href*='haryanajobs.in']")
            )

            # Fallback: grab all internal links
            if not candidates:
                candidates = [a for a in soup.select("a[href]")
                              if "haryanajobs.in" in a.get("href", "")]

            print(f"  haryanajobs candidates: {len(candidates)}")

            for a in candidates[:80]:
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
                state = "Central" if re.search(r'\bSSC\b|\bUPSC\b|\bRRB\b|\bRBI\b|\bSBI\b|\bNDA\b|\bCDS\b', title, re.I) else "State"
                org = title.split()[0]

                detail = extract_fields_from_detail(link) if link else {}
                pay = detail.get("pay") or infer_pay_from_text(title)
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
                    "payLevel": pay or "",
                    "category": "Govt",
                    "state": state,
                    "link": link,
                })
        except Exception as e:
            print(f"  haryanajobs error: {e}")

    print(f"  haryanajobs: {len(jobs)} jobs")
    return jobs
