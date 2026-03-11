import requests
import json

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

def send_file(token, chat_id, filepath, caption):
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(filepath, "rb") as f:
        requests.post(url, data={"chat_id": chat_id, "caption": caption}, files={"document": f})

def send_jobs(jobs, token, chat_id):
    total = len(jobs)
    with_vac = [j for j in jobs if j.get("vacancies", 0) > 0]

    summary = (
        f"🔔 <b>SSC English With Yash — Daily Job Alert</b>\n\n"
        f"📦 Total Jobs Scraped: <b>{total}</b>\n"
        f"✅ With Vacancies: <b>{len(with_vac)}</b>\n\n"
        f"<b>Top Jobs Today:</b>\n"
    )
    for j in sorted(with_vac, key=lambda x: -x.get("vacancies", 0))[:10]:
        summary += f"• {j.get('org','?')} — {j.get('vacancies',0)} vacancies\n"

    summary += "\n📎 Full JSON attached below. Import into your dashboard tool."
    send_message(token, chat_id, summary)

    send_file(token, chat_id, "jobs_data.json", f"jobs_data.json — {total} jobs ({len(with_vac)} with vacancies)")
    print("✅ Sent to Telegram!")
