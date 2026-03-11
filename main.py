import json
import os
from datetime import date
from scrapers.haryanajobs import scrape_haryanajobs
from scrapers.sarkarinetwork import scrape_sarkarinetwork
from scrapers.govtjobguru import scrape_govtjobguru
from telegram_sender import send_jobs

TODAY = str(date.today())

def main():
    print(f"🔍 Scraping jobs for {TODAY}...")
    all_jobs = []

    scrapers = [
        ("haryanajobs.in",    scrape_haryanajobs),
        ("sarkarinetwork.com", scrape_sarkarinetwork),
        ("govtjobguru.in",    scrape_govtjobguru),
    ]

    for source, fn in scrapers:
        try:
            jobs = fn()
            for j in jobs:
                j["source"] = source
                j["releaseDate"] = TODAY
                j["isNew"] = True
            all_jobs.extend(jobs)
            print(f"  ✅ {source}: {len(jobs)} jobs")
        except Exception as e:
            print(f"  ❌ {source}: {e}")

    # Save JSON file
    with open("jobs_data.json", "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)

    print(f"\n📦 Total: {len(all_jobs)} jobs saved to jobs_data.json")

    # Send to Telegram
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        send_jobs(all_jobs, token, chat_id)
    else:
        print("⚠️  No Telegram credentials found, skipping send.")

if __name__ == "__main__":
    main()
