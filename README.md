# AI-gri
### AI-Powered Agriculture Dashboard for Mindanao Farmers

[![Open Presentation](https://img.shields.io/badge/Pitch%20Deck-View%20PDF-blue)](https://drive.google.com/file/d/1gFhw6XHh7g5w4HMujNC-mX2xfghq-5dp/view?usp=drive_link)

An AI-powered agriculture monitoring and market intelligence dashboard built for Filipino farmers — specifically designed around the five top Mindanao commodities: coconut, banana, rice/palay, sugarcane, and corn. Built with Python and Streamlit, integrating Claude Sonnet for crop disease detection via computer vision, Open-Meteo for weather forecasting, and a market price intelligence module.

---

## The Problem

Filipino farmers — particularly in Mindanao, which produces over 40% of the Philippines' food supply — lack accessible tools for monitoring crop health, anticipating weather risks, and understanding market prices in one place. Disease identification is done by eye, weather is checked on consumer apps, and price data is scattered across government bulletins. Decisions are made on incomplete information.

---

## The Solution

A single-dashboard Streamlit application that gives a farmer or farm manager:

- **Crop Disease Detection** — upload a photo of a crop, get an AI diagnosis with severity, cause, treatment, and urgency
- **Weather Forecasting** — 5-day Open-Meteo forecast per field location, with rule-based Taglish farm advisories for heavy rain and strong wind
- **Market Price Intelligence** — commodity price tracking for the top Mindanao crops
- **Field Management** — register and manage multiple farm fields with location, crop type, and planting date

---

## My Contribution

This was a team project (3 members) built as part of Uplift Code Camp's Python for Data and AI Bootcamp Capstone.

My role covered:

- **Backend architecture** — designed and built the full SQLite database layer (users, fields, scan history tables), session-based authentication system, and app routing via `main.py`
- **AI integration** — engineered the Claude Sonnet vision pipeline for crop disease detection, returning structured JSON diagnosis results saved to scan history
- **Weather module** — integrated Open-Meteo API with per-field lat/lng routing and rule-based Taglish farm advisories
- **Brand and UI** — developed the AI-gri brand identity (logo, color system, typography) and the app's full UI design system in Streamlit
- **Pitch and storytelling** — architected the investor pitch narrative, framing AI-gri as a farm-gate intelligence platform within Mindanao's agri-supply chain

---

## Tech Stack

| Tool | Role |
|---|---|
| Streamlit | Frontend interface and app routing |
| Claude Sonnet (Anthropic API) | Crop disease detection via computer vision |
| Open-Meteo API | 5-day weather forecast (free, no key required) |
| SQLite (sqlite3) | Local database — users, fields, scan history |
| Python | Full backend pipeline |

---

## Focus Crops

Coconut · Banana · Rice/Palay · Sugarcane · Corn

---

## Pipeline Architecture
User logs in / registers
↓
Field Management — register farm fields with location + crop type
↓
Dashboard — market prices + weather overview
↓
Disease Detection — upload crop photo → Claude Sonnet vision → structured diagnosis
↓
Weather — Open-Meteo 5-day forecast per field → farm advisory
↓
Scan History — all past disease diagnoses saved per user/field

---

## Project Structure
ai-gri/
├── main.py               ← Entry point and page routing
├── login.py              ← Authentication
├── register.py           ← User registration
├── dashboard.py          ← Market prices + overview
├── fields.py             ← Farm field management
├── disease.py            ← Claude vision disease detection
├── weather.py            ← Open-Meteo weather + advisories
├── db.py                 ← SQLite database layer
├── .streamlit/
│   └── secrets.toml      ← API key configuration
├── requirements.txt
├── .gitignore
└── README.md

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/barcelonajames/ai-gri.git
cd ai-gri
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up API key
Create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "your_key_here"
```

### 4. Run the app
```bash
streamlit run main.py
```

Opens at **http://localhost:8501**

---

## Pitch Deck

Full project presentation including problem framing, solution walkthrough, system architecture, and market context:

[View Presentation (PDF)](https://drive.google.com/file/d/1gFhw6XHh7g5w4HMujNC-mX2xfghq-5dp/view?usp=drive_link)

[View on Google Slides](https://docs.google.com/presentation/d/1XzuJAV25PnOOjY-ATL2yOIjfLeYG6Pkn/edit?slide=id.p1#slide=id.p1)

---

*Built as part of Uplift Code Camp — Python for Data and AI Bootcamp Capstone, 2026*
