
# 🇮🇪 Irish Visa Decision Tracker

> **Live tool · 4,300+ users · zero advertising spend.**
> Real-time status checker for Irish visa applicants — built because the official portal doesn't tell you what week the Embassy is currently working on.

🔗 **Live app:** [huggingface.co/spaces/SR05/Delhi_Irish_visa_decisions](https://huggingface.co/spaces/SR05/Delhi_Irish_visa_decisions)
📊 **Usage (May 2026):** 4,119 all-time visits · 139 last month · 14 last week
🪪 **Built by:** [Shayshank Rathore](https://www.linkedin.com/in/shayshank-rathore/) · MSc AI, NCI Dublin

---

## The Problem

If you've applied for an Irish study or work visa from India, you know the pain:

- The official decision-status page is a long PDF that's updated weekly.
- It tells you which **application numbers** have been decided — but applicants don't know how to translate "what's the most recent week the Embassy decided?" into "should I be worried yet?"
- WhatsApp groups are full of guesses and rumours.

So I built a tool that scrapes the latest decision notices, parses them, and tells each applicant exactly where they stand — in seconds.

## How it works

```
┌─────────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Selenium scraper   │ ──▶ │  NLP / regex     │ ──▶ │  Streamlit UI    │
│  (weekly, headless) │     │  date extraction │     │  on HF Spaces    │
└─────────────────────┘     └──────────────────┘     └──────────────────┘
        ↑                            │
        │                            ▼
   official Irish              normalised JSON
   visa decision PDFs          (week-of, app-number ranges,
                                visa types)
```

1. A scheduled Selenium + BeautifulSoup job pulls the official decision notices.
2. NLP / regex extracts the week-ending date and the ranges of application numbers decided.
3. Streamlit serves a search box where the applicant enters their reference number — the app returns whether their application has been decided, and if not, how many weeks behind the Embassy is currently running.

## Stack

- **Frontend / UI:** Streamlit
- **Scraping:** Selenium, BeautifulSoup, requests
- **Parsing:** Python regex + light NLP
- **Hosting:** Hugging Face Spaces (free tier, persistent)
- **Storage:** Flat JSON snapshots checked into the repo for reproducibility

## Run locally

```bash
git clone https://github.com/shayshankr/Ireland_Visa_Status.git
cd Ireland_Visa_Status
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## What I learned shipping this

- **Word-of-mouth distribution is real.** I never advertised this tool. It crossed 4,000 visits because every visa WhatsApp group eventually shares the link.
- **Reliability > features.** Visa applicants are anxious. A tool that's wrong once is uninstalled forever.
- **Cheap infra is fine.** The whole stack runs on the free tier.

## Roadmap

- [ ] Multi-country support (UK, Schengen)
- [ ] Email alerts when "your week" is decided
- [ ] Historical decision-velocity charts (weeks-behind trend over time)

## License

Apache-2.0. Use the code freely; please credit if you fork the deployed product.

## About me

I'm a BI Developer & Data Engineer with 5+ years at Datafortune, plus an MSc in Artificial Intelligence from NCI Dublin. I'm currently in India and **open to opportunities** — AI Product, Data Engineering, or Technical PM roles.
📧 shayshankrathore05@gmail.com · 💼 [LinkedIn](https://www.linkedin.com/in/shayshank-rathore/) · 🌐 [GitHub](https://github.com/shayshankr)
