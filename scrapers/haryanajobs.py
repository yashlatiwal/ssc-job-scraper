import requests
from bs4 import BeautifulSoup
import re

URL = "https://haryanajobs.in/category/latest-jobs/"

def scrape_haryanajobs():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []

    for article in soup.select("article.post")[:30]:
        title_tag = article.select_one("h2.entry-title a, h3.entry-title a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag.get("href", "")

        # Extract vacancy count from title
        vac_match = re.search(r'(\d{2,6})\s*(Posts?|Vacancy|Vacancies)', title, re.I)
        vacancies = int(vac_match.group(1)) if vac_match else 0

        # Guess qualification
        qual = "Graduation"
        if re.search(r'\b10th\b|\bmatric\b', title, re.I): qual = "10th"
        elif re.search(r'\b12th\b|\binter\b', title, re.I): qual = "12th"

        # Guess state
        state_keywords = ["Haryana","Punjab","Rajasthan","UP","Bihar","HP","J&K","Delhi"]
        state = "State"
        for kw in state_keywords:
            if kw.lower() in title.lower():
                state = "State"
                break
        if re.search(r'\bSSC\b|\bUPSC\b|\bRRB\b|\bRBI\b|\bSBI\b|\bNDA\b|\bCDS\b', title, re.I):
            state = "Central"

        # Short org name (first word or acronym)
        org = title.split()[0] if title else "Unknown"

        jobs.append({
            "org": org,
            "fullOrg": "Unknown Organization",
            "post": title,
            "vacancies": vacancies,
            "qualification": qual,
            "age": "Not specified",
            "lastDate": "TBD",
            "lastDateFull": "TBD",
            "startDate": "TBD",
            "payLevel": "Not specified",
            "category": "Govt",
            "state": state,
            "link": link,
        })

    return jobs
