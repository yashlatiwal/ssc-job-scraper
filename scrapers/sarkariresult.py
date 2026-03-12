import requests
from bs4 import BeautifulSoup
import re, time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scrapers._base import find_vacancies, find_qualification, extract_fields_from_detail, infer_pay_from_text

URLS = [
    "https://www.sarkariresult.com/latestjob/",
    "https://sarkariresult.com/latestjob/",
    "https://www.sarkariresult.com/",
]

NOISE = re.compile(
    r'(Result\s*Declared|Answer\s*Key|Admit\s*Card|Exam\s*Date|Exam\s*City|'
    r'Score\s*Card|Cut\s*Off|Syllabus|Interview\s*Schedule|DV\s*Candidates|'
    r'Correction\s*Form|Edit\s*Form|Re-Exam|Postponed|Cancelled|'
    r'Home|About|Contact|Login|Register|Privacy|Disclaimer|Advertisement|'
    r'Latest\s*Result|Latest\s*Admit|Latest\s*Answer)',
    re.I
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://www.google.com/",
}

def scrape_sarkariresult():
    jobs = []
    seen = set()

    for url in URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            print(f"  sarkariresult → HTTP {resp.status_code} from {url}")
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # sarkariresult uses tables with class 'tablesorter' or plain tables
            # Jobs listed as <td><a href="...">Title</a></td>
            candidates = []
            for sel in [
                "table.tablesorter td a[href]",
                "#LatestJob td a[href]",
                ".job-section td a[href]",
                "table td a[href]",
                ".post-content a[href]",
                "article a[href]",
            ]:
                found = soup.select(sel)
                if found:
                    print(f"    '{sel}' → {len(found)}")
                    for a in found:
                        t = a.get_text(strip=True)
                        h = a.get("href", "")
                        if not h.startswith("http"):
                            h = "https://www.sarkariresult.com" + h if h.startswith("/") else ""
                        if t and len(t) > 10 and h:
                            candidates.append((t, h))

            # Dedup candidates
            seen_c = set()
            unique = [(t,h) for t,h in candidates if not (h in seen_c or seen_c.add(h))]
            print(f"  sarkariresult unique candidates: {len(unique)}")

            for title, link in unique[:100]:
                if link in seen: continue
                if NOISE.search(title): continue
                if not re.search(r'recruit|vacanc|notif|apply|post|bharti', title, re.I): continue
                seen.add(link)

                vac = find_vacancies(title)
                qual = find_qualification(title)
                state = "State" if re.search(
                    r'Haryana|Punjab|Rajasthan|Bihar|\bUP\b|Assam|Gujarat|Maharashtra|'
                    r'Odisha|Kerala|Bengal|Tamil|Karnataka|Andhra|Telangana|Himachal|'
                    r'Uttarakhand|Jharkhand|Chhattisgarh|Goa|Manipur|Tripura|Nagaland|'
                    r'Meghalaya|Mizoram|Arunachal|Sikkim|J&K|Ladakh|Delhi\b',
                    title, re.I
                ) else "Central"

                org_match = re.match(r'^([A-Z][A-Za-z\s&]+?)(?:\s*[\-,]|\s+Recruit|\s+Notif|\s+Online)', title)
                org = org_match.group(1).strip() if org_match else title.split()[0]

                detail = extract_fields_from_detail(link)
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
                print(f"  sarkariresult: {len(jobs)} jobs ✅")
                return jobs

        except Exception as e:
            print(f"  sarkariresult ERROR ({url}): {e}")

    print(f"  sarkariresult: 0 jobs ❌")
    return jobs
