import requests
from bs4 import BeautifulSoup
import re

URL = "https://govtjobguru.in/"

def scrape_govtjobguru():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []

    for a in soup.select("a[href]")[:60]:
        title = a.get_text(strip=True)
        link = a.get("href", "")

        if not title or len(title) < 15:
            continue
        if not re.search(r'recruit|vacanc|post|apply|job|exam|notif', title, re.I):
            continue

        vac_match = re.search(r'(\d{2,6})\s*(Posts?|Vacancy|Vacancies)', title, re.I)
        vacancies = int(vac_match.group(1)) if vac_match else 0

        qual = "Graduation"
        if re.search(r'\b10th\b|\bmatric\b', title, re.I): qual = "10th"
        elif re.search(r'\b12th\b|\binter\b', title, re.I): qual = "12th"

        state = "Central"
        if re.search(r'Haryana|Punjab|Rajasthan|Bihar|UP\b|Assam|Gujarat|Maharashtra', title, re.I):
            state = "State"

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
