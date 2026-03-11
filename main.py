import json
import os
from datetime import datetime, timedelta
from scrapers.haryanajobs import scrape_haryanajobs
from scrapers.sarkarinetwork import scrape_sarkarinetwork
from scrapers.govtjobguru import scrape_govtjobguru
from scrapers.freejobalert import scrape_freejobalert
from telegram_sender import send_jobs

def is_recent(job, days=10):
    try:
        d = datetime.strptime(job.get("releaseDate",""), "%Y-%m-%d")
        return d >= datetime.now() - timedelta(days=days)
    except:
        return True

def dedupe(jobs):
    seen = set()
    out = []
    for j in jobs:
        key = j.get("post","")[:60].lower().strip()
        if key not in seen:
            seen.add(key)
            out.append(j)
    return out

def run():
    today = datetime.now().strftime("%Y-%m-%d")
    all_jobs = []

    scrapers = [
        ("haryanajobs",    scrape_haryanajobs),
        ("sarkarinetwork", scrape_sarkarinetwork),
        ("govtjobguru",    scrape_govtjobguru),
        ("freejobalert",   scrape_freejobalert),
    ]

    for name, fn in scrapers:
        try:
            print(f"\n🔍 Scraping {name}...")
            jobs = fn()
            for j in jobs:
                j["releaseDate"] = today
                j["isNew"] = True
                j.setdefault("source", f"{name}.com")
            all_jobs.extend(jobs)
            print(f"  ✅ {len(jobs)} jobs from {name}")
        except Exception as e:
            print(f"  ❌ {name} failed: {e}")

    # Deduplicate
    all_jobs = dedupe(all_jobs)
    print(f"\n📦 Total after dedup: {len(all_jobs)} jobs")

    # Save JSON
    filename = f"jobs_data.json"
    with open(filename, "w") as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved to {filename}")

    # Send to Telegram
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        send_jobs(all_jobs, token, chat_id)
    else:
        print("⚠️ Telegram credentials not set")

if __name__ == "__main__":
    run()
