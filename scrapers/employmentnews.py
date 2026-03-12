import requests
from bs4 import BeautifulSoup
import re, time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import find_vacancies, find_qualification, extract_fields_from_detail, infer_pay_from_text

URL = "https://www.employmentnews.gov.in/NewVer/Pages/ActiveNotifications.aspx"
FALLBACK = "https://www.employmentnews.gov.in"

NOISE = re.compile(
    r'(Result|Answer\s*Key|Admit\s*Card|Exam\s*Date|Score\s*Card|'
    r'Cut\s*Off|Syllabus|Interview\s*Schedule|DV\s*Candidates|'
    r'Home|About|Contact|Archive|Subscribe|Login|Register|'
    r'Privacy|Disclaimer|Sitemap|Advertisement)',
    re.I
)

def scrape_employmentnews():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.google.com/",
    }
    jobs = []
    seen = set()

    for url in [URL, FALLBACK]:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            print(f"  employmentnews → HTTP {resp.status_code} from {url}")
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")

            # Try table rows first (their notification tables)
            candidates = []
            for a in soup.select("table a[href], .notification-list a[href], article a[href], a[href]"):
                t = a.get_text(strip=True)
                h = a.get("href", "")
                if not h.startswith("http"):
                    h = "https://www.employmentnews.gov.in" + h if h.startswith("/") else ""
                if t and len(t) > 10 and h:
                    candidates.append((t, h))

            print(f"  employmentnews candidates: {len(candidates)}")

            for title, link in candidates[:100]:
                if link in seen:
                    continue
                if NOISE.search(title):
                    continue
                if not re.search(r'recruit|vacanc|notif|apply|posts?', title, re.I):
                    continue
                seen.add(link)

                vac = find_vacancies(title)
                qual = find_qualification(title)
                state = "Central"  # employment news is mostly central govt
                if re.search(r'Haryana|Punjab|Rajasthan|Bihar|\bUP\b|Assam|Gujarat|Maharashtra|Odisha|Kerala', title, re.I):
                    state = "State"
                org = title.split()[0]

                detail = extract_fields_from_detail(link) if link else {}
                if not vac and detail.get("vac"):
                    vac = detail["vac"]
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

            if jobs:
                break  # got results, no need for fallback

        except Exception as e:
            print(f"  employmentnews error: {e}")

    print(f"  employmentnews: {len(jobs)} jobs")
    return jobs
