import json
import os
import requests
from datetime import date
from scrapers.haryanajobs import scrape_haryanajobs
from scrapers.sarkarinetwork import scrape_sarkarinetwork
from scrapers.govtjobguru import scrape_govtjobguru
from scrapers.freejobalert import scrape_freejobalert
from scrapers._base import infer_pay_from_text
from telegram_sender import send_jobs

TODAY = str(date.today())

def test_connectivity():
    """Quick check: can we reach each site at all?"""
    sites = [
        "https://haryanajobs.in/category/latest-jobs/",
        "https://sarkarinetwork.com/latest-update/",
        "https://govtjobguru.in/",
        "https://www.freejobalert.com/latest-notifications/",
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for url in sites:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            print(f"  🌐 {url[:45]} → HTTP {r.status_code} | {len(r.text)} chars")
        except Exception as e:
            print(f"  🌐 {url[:45]} → ERROR: {e}")

def main():
    print(f"🔍 Scraping jobs for {TODAY}...")
    print("\n--- Connectivity test ---")
    test_connectivity()
    print("--- End connectivity ---\n")

    all_jobs = []

    scrapers = [
        ("haryanajobs.in",    scrape_haryanajobs),
        ("sarkarinetwork.com", scrape_sarkarinetwork),
        ("govtjobguru.in",    scrape_govtjobguru),
        ("freejobalert.com",  scrape_freejobalert),
    ]

    for source, fn in scrapers:
        try:
            jobs = fn()
            print(f"  raw count from {source}: {len(jobs)}")
            for j in jobs:
                j["source"] = source
                j["releaseDate"] = TODAY
                j["isNew"] = True
                if not j.get("payLevel") or j["payLevel"] in ("", "Not specified"):
                    title = j.get("post", "") + " " + j.get("org", "")
                    inferred = infer_pay_from_text(title)
                    if inferred:
                        j["payLevel"] = inferred
            all_jobs.extend(jobs)
            print(f"  ✅ {source}: {len(jobs)} jobs")
        except Exception as e:
            import traceback
            print(f"  ❌ {source}: {e}")
            traceback.print_exc()

    print(f"\n📦 Total: {len(all_jobs)} jobs")

    with open("jobs_data.json", "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)

    with_pay = sum(1 for j in all_jobs if j.get("payLevel") and j["payLevel"] not in ("", "Not specified"))
    print(f"💰 With pay: {with_pay}/{len(all_jobs)}")

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        send_jobs(all_jobs, token, chat_id)
    else:
        print("⚠️  No Telegram credentials, skipping send.")

if __name__ == "__main__":
    main()
