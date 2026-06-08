# 🚀 CareerOS — AI Career Copilot MVP

An AI-powered job search assistant built with **Streamlit + FastAPI + Gemini 1.5 Flash (free tier)**.

---

## ✨ Features

| Module | What it does |
|---|---|
| 🔍 **JD Analyzer** | Match score, skill gaps, shortlist likelihood |
| ✨ **Resume Tailor** | AI-optimized summary, skills, experience bullets |
| 🤝 **Networking** | LinkedIn messages, recruiter emails, referral requests |
| 🎤 **Interview Coach** | Question bank, mock interview, AI feedback per answer |
| 📋 **Tracker** | Add/update/delete applications with status pipeline |
| 🏠 **Dashboard** | Funnel metrics, conversion rates, recent activity |

---

## 🛠️ Tech Stack (100% Free)

| Layer | Tool | Cost |
|---|---|---|
| LLM | Google Gemini 1.5 Flash | Free (15 RPM, 1M tokens/day) |
| Backend | FastAPI + Uvicorn | Free / open source |
| Frontend | Streamlit | Free / open source |
| Database | In-memory (dict store) | — |

---

## ⚡ Quick Start

### 1. Clone & install

```bash
git clone <your-repo>
cd careeros
pip install -r requirements.txt
```

### 2. Get your free Gemini API key

1. Go to https://aistudio.google.com/app/apikey
2. Click **"Create API Key"** (no credit card needed)
3. Copy the key

### 3. Set your API key

```bash
cp .env.example .env
# Edit .env and paste your key:
# GEMINI_API_KEY=AIza...
```

### 4. Run the backend (Terminal 1)

```bash
uvicorn backend.main:app --reload
```

Backend runs at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### 5. Run the frontend (Terminal 2)

```bash
streamlit run app.py
```

Frontend opens at: http://localhost:8501

---

## 📁 Project Structure

```
careeros/
├── app.py                          # Streamlit entry point
├── requirements.txt
├── .env.example
│
├── backend/
│   ├── main.py                     # FastAPI app + CORS
│   ├── routes/
│   │   ├── analyzer.py             # POST /analyze/
│   │   ├── tailor.py               # POST /tailor/
│   │   ├── network.py              # POST /network/
│   │   ├── interview.py            # POST /interview/questions
│   │   │                           # POST /interview/evaluate
│   │   └── tracker.py              # CRUD  /tracker/
│   └── utils/
│       ├── gemini.py               # Shared Gemini 1.5 Flash caller
│       └── store.py                # In-memory application store
│
└── frontend/
    ├── utils.py                    # API client + helper functions
    └── pages/
        ├── dashboard.py
        ├── analyzer.py
        ├── tailor.py
        ├── network.py
        ├── interview.py
        └── tracker.py
```

---

## 🔌 API Reference

### POST `/analyze/`
```json
{
  "job_description": "...",
  "resume": "..."
}
```
Returns: match_score, shortlist_likelihood, matching_skills, missing_skills, suggestions

### POST `/tailor/`
```json
{
  "target_role": "Senior Backend Engineer at Stripe",
  "resume": "...",
  "optimize_summary": true,
  "optimize_skills": true,
  "optimize_experience": true,
  "optimize_projects": false
}
```

### POST `/network/`
```json
{
  "message_type": "linkedin",
  "recipient_name": "Sarah Chen",
  "recipient_title": "Engineering Manager",
  "company": "Stripe",
  "target_role": "Backend Engineer",
  "your_background": "2 years fintech SWE..."
}
```
`message_type`: `linkedin` | `recruiter` | `referral` | `followup`

### POST `/interview/questions`
```json
{
  "role": "SWE II at Google",
  "interview_type": "mixed",
  "jd_snippet": "...",
  "num_questions": 5
}
```
`interview_type`: `technical` | `behavioral` | `mixed` | `product`

### POST `/interview/evaluate`
```json
{
  "question": "...",
  "answer": "...",
  "role": "...",
  "interview_type": "mixed"
}
```
Returns: score (1-10), strengths, improvements, ideal_answer_hint, overall_feedback

### GET/POST/PATCH/DELETE `/tracker/`
Full CRUD for application tracking.

---

## 🔮 Phase 2 Upgrades (Post-MVP)

- [ ] SQLite / PostgreSQL persistence
- [ ] User auth (Supabase free tier)
- [ ] PDF resume upload + parsing
- [ ] Email integration for auto follow-ups
- [ ] Analytics charts (Plotly)
- [ ] Gemini streaming for faster responses
- [ ] Docker + free deployment (Render / Railway)

---

## 📝 Gemini Free Tier Limits

| Limit | Value |
|---|---|
| Requests per minute | 15 RPM |
| Tokens per day | 1,000,000 |
| Context window | 1M tokens |

More than enough for MVP usage. Upgrade to Gemini API paid tier if needed.
