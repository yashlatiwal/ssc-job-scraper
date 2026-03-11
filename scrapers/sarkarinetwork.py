import requests
from bs4 import BeautifulSoup
import re
import time

LISTING_URL = "https://sarkarinetwork.com/latest-update/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

def extract_detail(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Sarkarinetwork uses tables for job details
        detail = {"vacancies":0,"age":"Not specified","lastDate":"TBD","lastDateFull":"TBD","payLevel":"Not specified","qualification":"Graduation"}
        
        # Try structured table first
        for row in soup.select("table tr"):
            cells = [td.get_text(strip=True) for td in row.find_all(["td","th"])]
            if len(cells) >= 2:
                key, val = cells[0].lower(), cells[1]
                if "vacanc" in key or "post" in key:
                    m = re.search(r'(\d[\d,]+)', val)
                    if m: detail["vacancies"] = int(m.group(1).replace(",",""))
                elif "age" in key:
                    m = re.search(r'(\d{2})\s*(?:to|-)\s*(\d{2})', val)
                    if m: detail["age"] = f"{m.group(1)}-{m.group(2)} Years"
                elif "last date" in key or "closing" in key:
                    detail["lastDate"] = detail["lastDateFull"] = val.strip()
                elif "pay" in key or "salary" in key:
                    m = re.search(r'level[- ]?(\d+)', val, re.I)
                    if m: detail["payLevel"] = f"Level {m.group(1)}"
                    else: detail["payLevel"] = val[:30]
                elif "qualif" in key or "education" in key:
                    if "10th" in val or "matric" in val.lower(): detail["qualification"] = "10th"
                    elif "12th" in val or "inter" in val.lower(): detail["qualification"] = "12th"

        # Fallback to text search
        text = soup.get_text(separator="\n")
        if detail["age"] == "Not specified":
            m = re.search(r'age\s*(?:limit)?[:\s]+(\d{2})\s*(?:to|-)\s*(\d{2})', text, re.I)
            if m: detail["age"] = f"{m.group(1)}-{m.group(2)} Years"
        if detail["lastDate"] == "TBD":
            m = re.search(r'last\s*date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{1,2}\s+\w+\s+\d{4})', text, re.I)
            if m: detail["lastDate"] = detail["lastDateFull"] = m.group(1).strip()
        return detail
    except: return {}

def scrape_sarkarinetwork():
    resp = requests.get(LISTING_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    links = []
    for a in soup.select("a[href]"):
        title = a.get_text(strip=True)
        href = a.get("href","")
        if not title or len(title) < 15 or "comment" in href: continue
        if not re.search(r'recruit|vacanc|post|apply|form|exam|notif', title, re.I): continue
        if re.match(r'^\d+$', title): continue
        if href.startswith("https://sarkarinetwork.com/") and href not in [l for _,l in links]:
            links.append((title, href))

    print(f"  sarkarinetwork: {len(links)} listings found")
    jobs = []
    for title, link in links[:30]:
        print(f"    → {title[:60]}")
        d = extract_detail(link)
        time.sleep(0.5)
        vt = re.search(r'(\d{2,6})\s*(Posts?|Vacancy|Vacancies)', title, re.I)
        state = "State" if re.search(r'Haryana|Punjab|Rajasthan|Bihar|\bUP\b|Assam|Gujarat|Maharashtra|\bHP\b|J&K|\bDelhi\b', title, re.I) else "Central"
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
            "state": state,
            "link": link,
        })
    return jobs
