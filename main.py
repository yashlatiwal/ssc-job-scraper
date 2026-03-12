import json, os, re, traceback
from datetime import date
from scrapers.sarkarinetwork import scrape_sarkarinetwork
from scrapers.govtjobguru import scrape_govtjobguru
from scrapers.sarkariresult import scrape_sarkariresult
from scrapers.rojgarresult import scrape_rojgarresult
from scrapers.sarkarijobfind import scrape_sarkarijobfind
from scrapers._base import infer_pay_from_text, find_vacancies
from telegram_sender import send_jobs

TODAY = str(date.today())


def normalize_title(t):
    """Strip year, punctuation, common suffixes for fuzzy matching."""
    t = t.lower()
    t = re.sub(r'\b202[0-9]\b', '', t)
    t = re.sub(r'(apply online|notification out|check details|last date.*$)', '', t)
    t = re.sub(r'[^a-z0-9\s]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def title_similarity(a, b):
    """Rough word-overlap similarity (0–1)."""
    wa = set(normalize_title(a).split())
    wb = set(normalize_title(b).split())
    if not wa or not wb:
        return 0
    return len(wa & wb) / max(len(wa), len(wb))


def dedup_jobs(jobs):
    """Remove duplicates — exact link OR very similar title (>70% word overlap)."""
    seen_links = set()
    seen_titles = []
    out = []
    for j in jobs:
        link = j.get("link", "")
        title = j.get("post", "")

        # Exact link dedup
        if link and link in seen_links:
            continue

        # Fuzzy title dedup — keep the one with more data (vacancies > 0 wins)
        duplicate = False
        for i, existing in enumerate(out):
            if title_similarity(title, existing.get("post", "")) > 0.70:
                duplicate = True
                # Merge: take best vacancy count and most complete data
                if j.get("vacancies", 0) > existing.get("vacancies", 0):
                    existing["vacancies"] = j["vacancies"]
                if not existing.get("age") and j.get("age"):
                    existing["age"] = j["age"]
                if not existing.get("lastDate") or existing["lastDate"] == "TBD":
                    if j.get("lastDate") and j["lastDate"] != "TBD":
                        existing["lastDate"] = j["lastDate"]
                        existing["lastDateFull"] = j["lastDate"]
                if not existing.get("payLevel") and j.get("payLevel"):
                    existing["payLevel"] = j["payLevel"]
                break

        if not duplicate:
            if link:
                seen_links.add(link)
            out.append(j)

    return out


def fetch_vacancy_from_google(title):
    """Search Google for vacancy count when it's missing from the page."""
    try:
        import requests
        from bs4 import BeautifulSoup
        query = re.sub(r'(apply online|notification out|check details)', '', title, flags=re.I).strip()
        query = query[:80] + " vacancies 2026"
        url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num=3"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        resp = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        snippet = soup.get_text(separator=" ")[:2000]
        v = find_vacancies(snippet)
        if v and not (2020 <= v <= 2030) and v < 100000:
            return v
    except Exception as e:
        print(f"    ⚠️ Google vacancy search failed: {e}")
    return 0


def main():
    print(f"🔍 Scraping jobs for {TODAY}...")
    all_jobs = []

    scrapers = [
        ("sarkariresult.com",   scrape_sarkariresult),
        ("rojgarresult.com",    scrape_rojgarresult),
        ("sarkarijobfind.com",  scrape_sarkarijobfind),
        ("govtjobguru.in",      scrape_govtjobguru),
        ("sarkarinetwork.com",  scrape_sarkarinetwork),
    ]

    for source, fn in scrapers:
        try:
            jobs = fn()
            for j in jobs:
                j["source"] = source
                j["releaseDate"] = TODAY
                j["isNew"] = True
                if not j.get("payLevel") or j["payLevel"] in ("", "Not specified"):
                    inferred = infer_pay_from_text(j.get("post", "") + " " + j.get("org", ""))
                    if inferred:
                        j["payLevel"] = inferred
            all_jobs.extend(jobs)
            print(f"  ✅ {source}: {len(jobs)} jobs")
        except Exception as e:
            print(f"  ❌ {source}: {e}")
            traceback.print_exc()

    # Health check — warn if a source returned 0
    print("\n📊 SOURCE HEALTH:")
    for source, fn in scrapers:
        count = sum(1 for j in all_jobs if j.get("source") == source)
        status = "✅" if count >= 3 else ("⚠️  LOW" if count > 0 else "❌ ZERO")
        print(f"  {status}  {source}: {count} jobs")

    # Dedup by link + fuzzy title similarity
    before = len(all_jobs)
    all_jobs = dedup_jobs(all_jobs)
    print(f"\n🔄 Dedup: {before} → {len(all_jobs)} jobs ({before - len(all_jobs)} removed)")

    # Fill missing vacancies via Google search
    missing_vac = [j for j in all_jobs if not j.get("vacancies", 0)]
    print(f"\n🔎 Fetching vacancies from Google for {len(missing_vac)} jobs...")
    filled = 0
    for j in missing_vac:
        v = fetch_vacancy_from_google(j.get("post", ""))
        if v:
            j["vacancies"] = v
            filled += 1
            print(f"  ✅ {j['org']}: {v} vacancies")
    print(f"  Filled {filled}/{len(missing_vac)} via Google")

    with_pay = sum(1 for j in all_jobs if j.get("payLevel") and j["payLevel"] not in ("", "Not specified"))
    with_vac = sum(1 for j in all_jobs if j.get("vacancies", 0) > 0)
    print(f"\n📦 Total: {len(all_jobs)} | 💰 Pay: {with_pay} | 👥 Vacancies: {with_vac}")

    with open("jobs_data.json", "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)
    print("✅ Saved jobs_data.json")

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        send_jobs(all_jobs, token, chat_id)
    else:
        print("⚠️  No Telegram credentials, skipping send.")

if __name__ == "__main__":
    main()
