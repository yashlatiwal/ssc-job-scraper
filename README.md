# SSC English With Yash — Job Scraper

Scrapes govt job sites daily at **10:00 AM IST** and sends a summary + `jobs_data.json` to your Telegram.

## Setup (5 minutes)

### 1. Fork / clone this repo to your GitHub

### 2. Add Telegram Bot secrets

Go to: **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Value |
|-------------|-------|
| `TELEGRAM_BOT_TOKEN` | Get from [@BotFather](https://t.me/BotFather) → /newbot |
| `TELEGRAM_CHAT_ID` | Get from [@userinfobot](https://t.me/userinfobot) |

### 3. Enable GitHub Actions

Go to the **Actions** tab in your repo and click **"I understand my workflows, go ahead and enable them"**

### 4. Test manually

Actions tab → **Daily Job Scraper** → **Run workflow** → Run

You'll get a Telegram message within ~60 seconds.

---

## How it works

- Runs every day at 10 AM IST via GitHub's free cron scheduler
- Scrapes: haryanajobs.in, sarkarinetwork.com, govtjobguru.in
- Sends summary + full `jobs_data.json` file to your Telegram
- You paste the JSON into your dashboard tool → jobs auto-filter to last 10 days

## Sites scraped

| Site | Type |
|------|------|
| haryanajobs.in | Haryana + Punjab state jobs |
| sarkarinetwork.com | Central + all-India jobs |
| govtjobguru.in | Mixed govt jobs |
