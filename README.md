# Daily Trading Decision Dashboard

Minimal production-ready Python project for a daily trading regime dashboard powered by `yfinance` and `Streamlit`.

## Features

- Fetches latest daily close prices for `QQQ` and `TQQQ`
- Classifies the market regime from the `QQQ` price
- Produces structured JSON output from `job.py`
- Displays prices, scenario, action, and notes in a Streamlit dashboard
- Includes Railway config for both the web dashboard and a scheduled daily job

## Project Structure

```text
.
├── app.py
├── job.py
├── railway.cron.json
├── railway.json
├── README.md
├── requirements.txt
└── trading_logic.py
```

## Local Development

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the daily job:

```bash
python job.py
```

Start the dashboard:

```bash
streamlit run app.py
```

## JSON Output

`job.py` prints JSON like:

```json
{
  "qqq": 701.25,
  "tqqq": 94.11,
  "scenario": "Strong Bull",
  "action": "Add aggressively to TQQQ",
  "timestamp": "2026-04-19T16:00:00+00:00"
}
```

## Scenario Rules

- `QQQ > 700`: Strong Bull
- `680 < QQQ <= 700`: Bull
- `630 < QQQ <= 680`: Neutral
- `600 < QQQ <= 630`: Weak
- `580 < QQQ <= 600`: Danger
- `QQQ <= 580`: Crash

## Railway Deployment

Railway cron jobs are service-scoped, so production deployment should use **two Railway services** from the same repo:

1. `dashboard-web` for the Streamlit UI
2. `dashboard-job` for the scheduled daily JSON refresh

### 1. Deploy the Web Dashboard

- Create a new Railway service from this repo.
- Keep the default root config file: `railway.json`.
- Railway will start the app with:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

### 2. Deploy the Daily Job

- Create a second Railway service from the same repo.
- In the service settings, set the config-as-code file path to `/railway.cron.json`.
- This service will run:

```bash
python job.py
```

- The cron schedule is `0 16 * * *`, which is **9:00 AM America/Los_Angeles on April 19, 2026** while Pacific Daylight Time is in effect.

### Important Railway Note

Railway cron schedules use **UTC**, not local time. If you want the job to always run at exactly 9:00 AM local time year-round, update the cron schedule during daylight-saving changes or replace the schedule with a timezone-aware external scheduler.

## Notes

- No API keys or secrets are required.
- `app.py` reads `latest_decision.json` when present and falls back to a live market fetch if the file does not exist yet.
- For production, consider attaching persistent storage or an external store if you want the generated JSON file shared reliably across services.
