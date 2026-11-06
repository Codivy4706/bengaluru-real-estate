# Bengaluru Real Estate Lead Intelligence & Outreach Platform

An end-to-end B2B lead generation, intelligence dashboard, website quality auditing, and WhatsApp outreach platform tailored for the Bengaluru real estate market.

---

## 🌟 Overview

This repository provides a complete pipeline to discover, analyze, verify, and reach out to real estate businesses (Builders, Property Developers, and Real Estate Agencies) across **5 major zones** in Bengaluru (North, South, East, West, and Central):

1. **Lead Scraping & Ingestion**: Fetches multi-zone real estate business profiles via the Google Places API (New) with an automated Karnataka RERA-verified baseline fallback.
2. **Centralized Excel Backend & Deduplication**: Multi-sheet workbook (`All_Companies` and zone-specific sheets) with deduplication, string sanitization, and structured lead tracking.
3. **Interactive Streamlit Dashboard**: Web UI for filtering leads by zone and business category, tracking verification status, viewing contact metrics, and downloading master Excel spreadsheets.
4. **Website Quality Audit Engine**: Evaluates lead websites on HTTP status, HTTPS security, load speed, page title, and meta descriptions, assigning weighted quality scores (0–100) and ratings.
5. **Automated WhatsApp Outreach Engine**: Dispatches personalized digital starter kit promotions and banner media via WhatsApp Web with built-in anti-spam throttling and status tracking.

---

## 📂 Repository Structure

```text
bengaluru-real-estate/
├── .env.example                     # Environment variables template
├── .gitignore                       # Production Git ignore rules (secrets, venv, caches, logs)
├── README.md                        # Project documentation
├── requirements.txt                 # Unified project dependencies
├── app.py                           # Streamlit Web Dashboard
├── scraper.py                       # Lead generation & Google Places API scraper
│
├── data/                            # Central data repository
│   ├── .gitkeep                     # Directory tracking
│   ├── bengaluru_real_estate_master.xlsx  # Master dataset (zone sheets + all companies)
│   ├── raw/                         # Raw scraped payloads
│   │   └── .gitkeep
│   └── processed/                   # Processed data outputs
│       └── .gitkeep
│
├── scripts/                         # Shared helper utilities
│   ├── __init__.py                  # Python package marker
│   └── scrapers_excel.py            # Deduplication & Excel export pipeline
│
├── website_quality_audit/           # Module: Website Health & SEO Quality Auditor
│   ├── __init__.py                  # Package marker
│   ├── .env.example                 # Optional module environment variables template
│   ├── app.py                       # Batch website auditor script
│   ├── scoring.py                   # Scoring algorithms & rating rules
│   ├── website_checker.py           # HTTP/SSL status and metadata extraction
│   ├── requirements.txt             # Audit module dependencies
│   ├── input/                       # Audit input files
│   │   ├── .gitkeep
│   │   └── bengaluru_real_estate_master.xlsx
│   └── output/                      # Audit output reports
│       ├── .gitkeep
│       ├── website_audit_full.xlsx
│       └── website_audit_test.xlsx
│
└── whatsapp_automation/             # Module: Targeted WhatsApp Outreach Engine
    ├── __init__.py                  # Package marker
    ├── auto.py                      # WhatsApp messaging script with anti-spam delays
    ├── banner.jpeg                  # Promotional starter kit banner image
    ├── Exposys Real Estate Bangalore.xlsx  # Multi-agent lead tracking sheet
    └── requirements.txt             # WhatsApp automation dependencies
```

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- **Python**: Version 3.10 or higher
- **Git**

### 2. Clone the Repository
```bash
git clone https://github.com/Codivy4706/bengaluru-real-estate.git
cd bengaluru-real-estate
```

### 3. Create and Activate a Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to create your local `.env` file:
```bash
cp .env.example .env
```
Open `.env` and set your Google Places API Key:
```env
GOOGLE_PLACES_API_KEY=your_actual_api_key_here
```
> *Note:* If no API key is configured or billing is inactive, the scraper automatically falls back to the verified Karnataka RERA baseline dataset.

---

## 🛠️ Usage Guide

### 1. Run the Lead Scraper
Fetches leads across all Bengaluru zones and populates `data/bengaluru_real_estate_master.xlsx`:
```bash
python scraper.py
```

### 2. Launch the Streamlit Dashboard
Start the interactive dashboard to filter and inspect leads:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` to:
- Filter leads by **Zone** (North, South, East, West, Central) or **Business Category**.
- Inspect contact information, addresses, website links, and verification status.
- Download the master Excel report with one click.

### 3. Run the Website Quality Audit
Evaluate the digital presence and SEO readiness of scraped real estate leads:
```bash
python website_quality_audit/app.py
```
- Reads URLs from `data/bengaluru_real_estate_master.xlsx`.
- Audits HTTP status, SSL certificate, page titles, meta descriptions, and load speeds.
- Saves the final scored report to `website_quality_audit/output/website_audit_full.xlsx`.

### 4. Run Automated WhatsApp Outreach
Execute targeted, personalized outreach to verified phone numbers:
```bash
python whatsapp_automation/auto.py
```
- Prompts for the agent's sheet name (e.g., `Divyansh`, `Akash`, `Mahesh`, `Vinuthna`).
- Cleans and formats phone numbers to standard E.164 (`+91...`).
- Transmits introductory offers with the `banner.jpeg` attachment.
- Implements randomized sleep delays (1–3 seconds) to protect account reputation.
- Updates the spreadsheet in real time with status tags (`sent`, `invalid number`, `no whatsapp`).

---

## 📊 Scoring Rubric (Website Quality Audit)

Websites are evaluated against a 100-point rubric:

| Criterion | Points | Description |
| :--- | :---: | :--- |
| **Availability** | 30 | Website is online and returns HTTP 200 |
| **HTTPS Security** | 25 | Valid SSL certificate and HTTPS redirection |
| **Page Title** | 20 | Meaningful `<title>` tag present for SEO |
| **Meta Description** | 15 | `<meta name="description">` configured for search indexing |
| **Response Latency** | 10 | ≤ 2s (10 pts), ≤ 4s (7 pts), ≤ 6s (4 pts), > 6s (0 pts) |
| **Total** | **100** | **Ratings: Excellent (≥90), Good (≥75), Needs Improvement (≥50), Poor (<50)** |

---

## 🗺️ Geographic Coverage (Bengaluru)

- **North Zone**: Yelahanka, Rajanukunte, Hebbal, Devanahalli, Jakkur, Thanisandra
- **South Zone**: Electronic City, JP Nagar, Bannerghatta Road, BTM, Kanakapura Road
- **East Zone**: Whitefield, Marathahalli, Sarjapur Road, KR Puram, Varthur
- **West Zone**: Vijayanagar, Rajajinagar, Nagarbhavi, Kengeri, Yeshwanthpur
- **Central Zone**: MG Road, Indiranagar, Koramangala, Jayanagar, Shivajinagar

---

## 🔒 Security & Best Practices

- **Never Commit Secrets**: All `.env` files are strictly excluded via `.gitignore`.
- **Anti-Spam Compliance**: WhatsApp automation respects rate limits and opt-out requests (`STOP`).
- **Data Integrity**: Automated deduplication preserves existing leads while appending newly discovered records.

---

## 📄 License
This project is proprietary and developed for internal real estate intelligence and outreach operations.
