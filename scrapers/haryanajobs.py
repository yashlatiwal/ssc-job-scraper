import requests
from bs4 import BeautifulSoup
import re
import time

LISTING_URL = "https://haryanajobs.in/category/latest-jobs/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

def extract_detail(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator="\n")
        detail = {"vacancies":0,"age":"Not specified","lastDate":"TBD","lastDateFull":"TBD","payLevel":"Not specified","qualification":"Graduation"}

        m = re.search(r'(?:vacancy|vacancies|posts?)[:\s]+(\d[\d,]+)', text, re.I)
        if not m: m = re.search(r'(\d[\d,]+)\s+(?:posts?|vacancies|vacancy)', text, re.I)
        if m: detail["vacancies"] = int(m.group(1).replace(",",""))

        m = re.search(r'age\s*(?:limit)?[:\s]+(\d{2})\s*(?:to|-)\s*(\d{2})', text, re.I)
        if m: detail["age"] = f"{m.group(1)}-{m.group(2)} Years"

        m = re.search(r'last\s*date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{1,2}\s+\w+\s+\d{4})', text, re.I)
        if m: detail["lastDate"] = detail["lastDateFull"] = m.group(1).strip()

        m = re.search(r'(?:pay scale|salary|pay level)[:\s]+(?:level[- ]?(\d+)|rs\.?\s*([\d,]+))', text, re.I)
        if m: detail["payLevel"] = f"Level {m.group(1)}" if m.group(1) else f"₹{m.group(2)}"

        if re.search(r'\b10th\b|matriculation', text, re.I): detail["qualification"] = "10th"
        elif re.search(r'\b12th\b|intermediate', text, re.I): detail["qualification"] = "12th"
        return detail
    except: return {}

def scrape_haryanajobs():
    resp = requests.get(LISTING_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = [(a.get_text(strip=True), a["href"]) for a in soup.select("h2.entry-title a, h3.entry-title a") if a.get("href")]
    if not links:
        links = [(a.get_text(strip=True), a["href"]) for a in soup.select("article a[href]") if len(a.get_text(strip=True)) > 20][:30]
    print(f"  haryanajobs: {len(links)} listings found")
    jobs = []
    for title, link in links[:25]:
        print(f"    → {title[:60]}")
        d = extract_detail(link)
        time.sleep(0.5)
        vt = re.search(r'(\d{2,6})\s*(Posts?|Vacancy|Vacancies)', title, re.I)
        jobs.append({
            "org": title.split()[0],
            "fullOrg": title.split(":")[0].strip() if ":" in title else title.split()[0],
            "post": title,
            "vacancies": d.get("vacancies") or (int(vt.group(1)) if vt else 0),
            "qualification": d.get("qualification","Graduation"),
            "age": d.get("age","Not specified"),
            "lastDate": d.get("lastDate","TBD"),
            "lastDateFull": d.get("lastDateFull","TBD"),
            "startDate": "TBD",
            "payLevel": d.get("payLevel","Not specified"),
            "category": "Govt",
            "state": "Central" if re.search(r'\bSSC\b|\bUPSC\b|\bRRB\b|\bRBI\b|\bNavy\b|\bArmy\b', title, re.I) else "State",
            "link": link,
        })
    return jobs
