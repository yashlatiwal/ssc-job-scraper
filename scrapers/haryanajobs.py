import requests
from bs4 import BeautifulSoup
import re, time
from scrapers._base import clean, extract_from_tables, merge_with_text

LISTING_URL = "https://haryanajobs.in/category/latest-jobs/"
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

def scrape_haryanajobs():
    resp = requests.get(LISTING_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = [(a.get_text(strip=True), a["href"]) for a in soup.select("h2.entry-title a, h3.entry-title a, .entry-title a") if a.get("href")]
    if not links:
        seen = set()
        for a in soup.select("a[href]"):
            t = a.get_text(strip=True); h = a.get("href","")
            if len(t) > 20 and h.startswith("https://haryanajobs.in/") and h not in seen:
                links.append((t,h)); seen.add(h)
    print(f"  haryanajobs: {len(links)} listings")
    jobs = []
    for title, link in links[:25]:
        print(f"    → {title[:70]}")
        d = extract_detail(link); time.sleep(0.5)
        vt = re.search(r'(\d{2,6})\s*(Posts?|Vacancy|Vacancies)', title, re.I)
        jobs.append({"org":title.split()[0],"fullOrg":title.split(":")[0].strip() if ":" in title else title.split()[0],
            "post":title,"vacancies":d["vacancies"] or (int(vt.group(1)) if vt else 0),
            "qualification":d["qualification"],"age":d["age"],"lastDate":d["lastDate"],
            "lastDateFull":d["lastDateFull"],"startDate":"TBD","payLevel":d["payLevel"],
            "category":"Govt","state":"Central" if re.search(r'\bSSC\b|\bUPSC\b|\bRRB\b|\bRBI\b|\bNavy\b|\bArmy\b|\bNDA\b', title, re.I) else "State",
            "link":link,"source":"haryanajobs.in"})
    return jobs
