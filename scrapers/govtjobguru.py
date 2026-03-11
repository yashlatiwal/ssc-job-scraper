import requests
from bs4 import BeautifulSoup
import re, time
from scrapers._base import clean, extract_from_tables, merge_with_text

LISTING_URL = "https://govtjobguru.in/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

def extract_detail(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        detail = extract_from_tables(soup)
        text = clean(soup.get_text(separator=" "))
        return merge_with_text(detail, text)
    except Exception as e:
        print(f"    ⚠️ {e}")
        return {"vacancies":0,"age":"Not specified","lastDate":"TBD","lastDateFull":"TBD","payLevel":"Not specified","qualification":"Graduation"}

def scrape_govtjobguru():
    resp = requests.get(LISTING_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    seen = set(); links = []
    for a in soup.select("a[href]"):
        t = a.get_text(strip=True); h = a.get("href","")
        if not t or len(t) < 15: continue
        if not re.search(r'recruit|vacanc|post|apply|form|exam|notif|job', t, re.I): continue
        if h.startswith("https://govtjobguru.in/") and h != LISTING_URL and h not in seen:
            links.append((t,h)); seen.add(h)
    print(f"  govtjobguru: {len(links)} listings")
    jobs = []
    for title, link in links[:25]:
        print(f"    → {title[:70]}")
        d = extract_detail(link); time.sleep(0.5)
        vt = re.search(r'(\d{2,6})\s*(Posts?|Vacancy|Vacancies)', title, re.I)
        state = "State" if re.search(r'Haryana|Punjab|Rajasthan|Bihar|\bUP\b|Assam|Gujarat|Maharashtra|\bHP\b|Odisha|Kerala', title, re.I) else "Central"
        jobs.append({"org":title.split()[0],"fullOrg":title.split(":")[0].strip() if ":" in title else title.split()[0],
            "post":title,"vacancies":d["vacancies"] or (int(vt.group(1)) if vt else 0),
            "qualification":d["qualification"],"age":d["age"],"lastDate":d["lastDate"],
            "lastDateFull":d["lastDateFull"],"startDate":"TBD","payLevel":d["payLevel"],
            "category":"Govt","state":state,"link":link,"source":"govtjobguru.in"})
    return jobs
