# CommentGuard AI 🛡️

## Contributors
### 1.Mohammed Taha Hakim mohdtaha_h@hotmail.com @tahalikescoding
### 2.Shikhar Saini shikharsaini2408@gmail.com @Pestboi99
### 3.Muhammed Sahil msahilstack@gmail.com @msahilquant
### 4.Harshit Srivastava f20260233@dubai.bits-pilani.ac.in @HarshitSrivastava0951

**CommentGuard AI** is an advanced bot account detection and security operations (SOC) dashboard for YouTube content creators and community moderators. It analyzes video comment sections in real-time, identifies likely bot accounts and coordinated Sybil campaigns, and provides transparent forensic explanations for every flagged account — helping creators moderate spam, scam links, and coordinated attacks without manually sifting through hundreds of comments.

🔗 **Live Demo**: [https://bot-account-detection-sysrem-1.onrender.com](https://bot-account-detection-sysrem-1.onrender.com)
> Hosted on Render's free tier — the first load may take 30–50 seconds if the instance has spun down from inactivity.

---

## 🚀 Key Features

### 1. YouTube Data API v3 & Realistic Offline Demo Fallback
- Paste any YouTube video URL or ID (e.g. `https://www.youtube.com/watch?v=...` or `https://youtu.be/...`).
- Optional YouTube Data API v3 key integration for live comment fetching.
- Intelligent fallback to curated, realistic mock datasets (`Crypto Scam Surge`, `Tech Review Raid`, `Clean Baseline`) so the dashboard works completely offline without an internet connection or API quota limits.

### 2. Multi-Signal Weighted Bot Scoring Engine (0 - 100)
Evaluates each commenter across 7 weighted behavioral, temporal, and linguistic signals:
- **Account Age / Sleeper Signals (Max 25 pts)**: Identifies brand-new accounts (<3 days, <14 days) and dormant accounts (>2 years) hijacked to post scam links.
- **Generic / Random Username Patterns (Max 20 pts)**: Identifies auto-generated identifiers with trailing long digit strings (`User88391024`, `Crypto_Helper_9812`).
- **Default / Missing Profile Picture (Max 20 pts)**: Identifies default silhouettes and uncustomized identicons.
- **Publish Timing Burst (Max 30 pts)**: Detects comments posted within 15s or 60s of video publication.
- **Phishing Links & High-Risk Keywords (Max 35 pts)**: Identifies malicious URLs (`t.me`, `wa.me`, `bit.ly`, scam domains) and keywords (`crypto`, `whatsapp`, `giveaway`, `gift card`, `passive income`, `won an iphone`, `sub 4 sub`).
- **Emoji Density & All-Caps Formatting (Max 15 pts)**: Identifies high emoji density (🔥🚀💰🎉) and shouty all-caps spam text (>50% uppercase).
- **Near-Duplicate / Copy-Paste Text (Max 25 pts)**: Computes batch-wide string similarity (Levenshtein & normalized sequence matching) to flag copy-paste spam rings.

**Classification Tiers**:
- 🟢 **Likely Human** (0 – 30)
- 🟡 **Suspicious** (31 – 65)
- 🔴 **Likely Bot** (66 – 100)

### 3. Real-Time Security Operations (SOC) Dashboard
- **Summary Stat Cards**:
  - Total Comments Analyzed
  - Likely Bots Detected (Count & Percentage)
  - Suspected Coordinated Accounts (Sybil Rings)
  - Average Bot Score (with color-coded gauge bar)
- **Live Comment Feed Table**:
  - Color-coded left risk border and risk badges.
  - Formatted publish timestamps with delta offset badges (e.g. `⚡ +14s after upload`).
  - Signal pills highlighting triggered rules.
  - Real-time search by username, handle, or comment text.
  - Sorting by Highest Bot Score, Lowest Bot Score, Fastest After Upload, or Most Recent.

### 4. Coordinated Campaign Detector (Right Sidebar)
- Groups flagged accounts that share near-identical comment text, identical external links/WhatsApp contacts, or synchronized time bursts.
- Displays clusters (e.g. `Cluster A: Crypto Recovery Ring (5 accounts, 12s burst)`) with sample text previews and shared traits.
- **"Inspect Cluster"** button to filter and highlight the ring in the live comment table.

### 5. Live Test Injector Panel (Interactive Demo Mode)
Simulate live bot attacks on command without waiting for real bots:
- **"Inject Spam Bot"**: Injects a single generic bot with external links and default avatar.
- **"Inject Coordinated Campaign"**: Injects 5 coordinated accounts at once to immediately trigger the Campaign Detector.
- **"Inject Sleeper Account"**: Injects a 6-year-old dormant account posting a sudden crypto phishing link.
- Injected rows slide in with a pulsing glow and update summary metrics in real-time.

### 6. Forensic Account Inspector (Slide-Over Drawer)
- Click **"Inspect"** on any account to view:
  - Account avatar, handle, and Channel ID.
  - Radial risk meter and score gauge.
  - Itemized point breakdown explaining exactly why points were added.
  - Duplicate match viewer listing matched accounts and similarity percentages.
  - Copy Channel ID to clipboard for YouTube Studio moderation.
  - Simulate Shadowban action.

### 7. Model Explainability Panel
- Visual distribution of feature weight contributions across the analyzed batch.
- Transparent display showing that detection is rule-governed rather than an opaque black box.

### 8. Export Capabilities
- One-click export of flagged accounts and clusters to **JSON** or **CSV** formats for YouTube Studio blocklists.

---

## 🛠️ Architecture & Tech Stack

- **Backend**: Python 3.14 + Flask, served in production via Gunicorn
- **Frontend**: Vanilla HTML5, Vanilla CSS3 (Custom Dark SOC Theme, Glassmorphism, CSS Grid & Flexbox), Vanilla JavaScript (Modular ES6)
- **Data Layer**: YouTube Data API v3 + Built-in Realistic Mock Data Presets
- **Deployment**: Render (free tier, auto-deploys from GitHub `main` branch)

```text
bot_account-detection-system/
│
├── app.py                     # Flask server and REST API endpoints
├── requirements.txt           # Python dependencies
├── Procfile                   # Gunicorn start command for deployment
├── README.md                  # System documentation
│
├── bot_detector/
│   ├── __init__.py            # Package exports
│   ├── scoring_engine.py      # Multi-signal weighted scoring & explainability
│   ├── campaign_detector.py   # Sybil cluster & coordinated ring detection
│   ├── youtube_service.py     # YouTube Data API v3 client + fallback logic
│   └── mock_data.py           # Realistic mock presets & injection templates
│
├── static/
│   ├── css/
│   │   ├── style.css          # Design system, color tokens, and navbar
│   │   └── dashboard.css      # Grid layout, tables, drawer, cards, animations
│   └── js/
│       ├── app.js             # Main controller, state management, event routing
│       ├── components.js      # Render engine (tables, badges, drawer, stats)
│       ├── injector.js        # Live fraud injector logic
│       └── explainability.js  # Feature importance bar charts
│
└── templates/
    └── index.html             # Single-page dashboard application
```

---

## 💻 Running Locally

1. **Clone the repo and install dependencies**:
```bash
git clone https://github.com/tahalikescoding/bot_account-detection-system.git
cd bot_account-detection-system
pip install -r requirements.txt
```

2. **(Optional) Set a YouTube Data API v3 key** if you want live comment fetching instead of the demo presets:
```bash
export YOUTUBE_API_KEY=your_api_key_here      # macOS/Linux
set YOUTUBE_API_KEY=your_api_key_here          # Windows (cmd)
```
Without this, the app still works fully using built-in demo presets and a real-time scraping fallback.

3. **Start the application**:
```bash
python app.py
```

4. **Open in browser**:
Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

The dashboard will automatically boot up with the **Crypto Scam Surge** demo preset pre-loaded so you can explore all features immediately.

---

## ☁️ Deployment

This project is deployed on **Render** using:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Environment Variable**: `YOUTUBE_API_KEY` (optional — enables live YouTube comment analysis; without it, the app uses realistic demo/mock data)
