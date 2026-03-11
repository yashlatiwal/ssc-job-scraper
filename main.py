import json
import os
from datetime import date
from scrapers.haryanajobs import scrape_haryanajobs
from scrapers.sarkarinetwork import scrape_sarkarinetwork
from scrapers.govtjobguru import scrape_govtjobguru
from scrapers.freejobalert import scrape_freejobalert
from scrapers._base import infer_pay_from_text
from telegram_sender import send_jobs

TODAY = str(date.today())

def main():
    print(f"🔍 Scraping jobs for {TODAY}...")
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
            for j in jobs:
                j["source"] = source
                j["releaseDate"] = TODAY
                j["isNew"] = True
                # Fallback: infer pay from title if scraper couldn't find it
                if not j.get("payLevel") or j["payLevel"] == "Not specified":
                    title = j.get("post", "") + " " + j.get("org", "")
                    inferred = infer_pay_from_text(title)
                    if inferred:
                        j["payLevel"] = inferred
            all_jobs.extend(jobs)
            print(f"  ✅ {source}: {len(jobs)} jobs")
        except Exception as e:
            print(f"  ❌ {source}: {e}")

    with open("jobs_data.json", "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)

    with_pay = sum(1 for j in all_jobs if j.get("payLevel") and j["payLevel"] != "Not specified")
    print(f"\n📦 Total: {len(all_jobs)} jobs | With pay: {with_pay}/{len(all_jobs)}")

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        send_jobs(all_jobs, token, chat_id)
    else:
        print("⚠️  No Telegram credentials, skipping send.")

if __name__ == "__main__":
    main()
