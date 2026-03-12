import requests
from bs4 import BeautifulSoup
import re, time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import find_vacancies, find_qualification, extract_fields_from_detail, infer_pay_from_text

URLS = [
    "https://www.employmentnews.gov.in/NewVer/Pages/ActiveNotifications.aspx",
    "https://employmentnews.gov.in/NewVer/Pages/ActiveNotifications.aspx",
    "https://www.employmentnews.gov.in",
]

NOISE = re.compile(
    r'(Result|Answer\s*Key|Admit\s*Card|Exam\s*Date|Score\s*Card|'
    r'Cut\s*Off|Syllabus|Interview\s*Schedule|DV\s*Candidates|'
    r'Home|About|Contact|Archive|Subscribe|Login|Register|'
    r'Privacy|Disclaimer|Sitemap|Advertisement|Skip\s*to|Back\s*to)',
    re.I
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://www.google.com/",
}

def scrape_employmentnews():
    jobs = []
    seen = set()

    for url in URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            print(f"  employmentnews → HTTP {resp.status_code} from {url}")
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # Try multiple selectors in priority order
            candidates = []
            for sel in [
                "table td a[href]",
                ".notification a[href]",
                "ul li a[href]",
                "article a[href]",
                "a[href*='employmentnews']",
                "a[href*='Notifications']",
                "a[href*='notification']",
            ]:
                found = soup.select(sel)
                if found:
                    print(f"    selector '{sel}' → {len(found)} links")
                    for a in found:
                        t = a.get_text(strip=True)
                        h = a.get("href", "")
                        if not h.startswith("http"):
                            h = "https://www.employmentnews.gov.in" + h if h.startswith("/") else ""
                        if t and len(t) > 10 and h:
                            candidates.append((t, h))

            # Deduplicate candidates
            seen_c = set()
            unique = []
            for t, h in candidates:
                if h not in seen_c:
                    seen_c.add(h)
                    unique.append((t, h))
            candidates = unique
            print(f"  employmentnews unique candidates: {len(candidates)}")

            for title, link in candidates[:80]:
                if link in seen:
                    continue
                if NOISE.search(title):
                    continue
                if not re.search(r'recruit|vacanc|notif|apply|post', title, re.I):
                    continue
                seen.add(link)

                vac = find_vacancies(title)
                qual = find_qualification(title)
                state = "State" if re.search(
                    r'Haryana|Punjab|Rajasthan|Bihar|\bUP\b|Assam|Gujarat|Maharashtra|Odisha|Kerala|Bengal|Tamil|Karnataka|Andhra|Telangana|Himachal|Uttarakhand',
                    title, re.I
                ) else "Central"

                # Extract org from title (before first comma or dash)
                org_match = re.match(r'^([A-Z][A-Za-z\s&]+?)(?:\s*[\-,]|\s+Recruit|\s+Notif)', title)
                org = org_match.group(1).strip() if org_match else title.split()[0]

                detail = extract_fields_from_detail(link) if link else {}
                if not vac and detail.get("vac"):
                    vac = detail["vac"]
                pay = detail.get("pay") or infer_pay_from_text(title)
                time.sleep(0.3)

                jobs.append({
                    "org": org,
                    "fullOrg": org,
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
                print(f"  employmentnews: {len(jobs)} jobs ✅")
                return jobs

        except Exception as e:
            print(f"  employmentnews ERROR ({url}): {e}")
            continue

    print(f"  employmentnews: {len(jobs)} jobs (all URLs failed or 0 results)")
    return jobs
