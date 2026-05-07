# 🇮🇪 Ireland Visa Status Checker — New Delhi Embassy

A Streamlit app that lets Irish visa applicants instantly check whether their application has been decided by the **New Delhi Embassy**, without manually scanning the official PDF.

Data is sourced live from [ireland.ie](https://www.ireland.ie/en/india/newdelhi/services/visas/processing-times-and-decisions/) and refreshes every hour.

🔗 **Live app:** [huggingface.co/spaces/SR05/Delhi_Irish_visa_decisions](https://huggingface.co/spaces/SR05/Delhi_Irish_visa_decisions)
📊 **Usage (May 2026):** 4,119+ all-time visits
🪪 **Built by:** [Shayshank Rathore](https://www.linkedin.com/in/shayshank-rathore/) · MSc AI, NCI Dublin

---

## The Problem

If you've applied for an Irish study or work visa from India, you know the pain:

- The official decision-status page is a long ODS spreadsheet updated weekly.
- It lists application numbers that have been decided — but not in a searchable way.
- WhatsApp groups are full of guesses and rumours.

This tool scrapes the latest decision file, parses it, and tells each applicant exactly where they stand — in seconds.

---

## Features

- Auto-fetches the latest visa decisions ODS file from ireland.ie
- Search by application number: `63690452`, `IRL63690452`, or `irl63690452`
- Colour-coded result — green for approved ✅, red for refused ❌
- If your number isn't found yet, shows the nearest processed numbers above and below yours using **binary search**
- Displays total decisions, approvals, and refusals at a glance
- Full dataset available as a CSV download

## How to Use

1. Enter your 8-digit application number (with or without the `IRL` prefix)
2. Press Enter or click elsewhere to search
3. If your number isn't in the list, the app shows the nearest processed applications so you can gauge where the Embassy is up to

---

## Run Locally

```bash
git clone https://github.com/shayshankr/Ireland_Visa_Status.git
cd Ireland_Visa_Status
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Requirements

- Python 3.10+
- streamlit, requests, pandas, odfpy, beautifulsoup4

## File Structure

```
├── streamlit_app.py   # Main app — scraping, parsing, search UI
└── requirements.txt   # Python dependencies
```

## Data Source

Visa decision data is published weekly by the Irish Embassy, New Delhi:
[https://www.ireland.ie/en/india/newdelhi/services/visas/processing-times-and-decisions/](https://www.ireland.ie/en/india/newdelhi/services/visas/processing-times-and-decisions/)

Current dataset: **14,013 decisions** from 1 January 2026 to 5 May 2026 · 11,985 Approved · 2,028 Refused.

---

## Roadmap

- [ ] Email/WhatsApp alerts when your application week is decided
- [ ] Multi-embassy support (Abu Dhabi, London)
- [ ] Historical decision-velocity charts (weeks-behind trend over time)

## About

Built by **Shayshank Rathore** — BI Developer & Data Engineer, MSc AI (NCI Dublin).
📧 shayshankrathore05@gmail.com · 💼 [LinkedIn](https://www.linkedin.com/in/shayshank-rathore/) · 🌐 [GitHub](https://github.com/shayshankr)

## License

Apache-2.0. Use the code freely; please credit if you fork the deployed product.
