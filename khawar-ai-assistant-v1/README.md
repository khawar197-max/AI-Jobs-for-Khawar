# 🤖 Khawar AI Career Assistant — V1

A Streamlit-based personal AI assistant for discovering:

- International and Pakistan jobs
- Remote opportunities
- Fully funded PhD positions
- Scholarships and funded research positions
- Opportunity-to-profile matching
- Tailored ATS-friendly CVs
- Job/PhD cover letters
- Saved opportunities

## 1. Features

### Opportunity discovery
The app searches the web for jobs, PhDs and scholarships using configurable search queries.

### AI matching
Groq analyzes search candidates against `data/profile.json` and produces a transparent fit score and reasons.

### CV tailoring
The assistant creates a truthful, opportunity-specific CV from your profile.

### Cover letters
It generates a targeted application letter for each selected opportunity.

### Pakistan filter
You can exclude Municipal Officer/local-government roles in Pakistan when searching for a career change.

## 2. Important limitation

V1 is a research/discovery assistant, not an autonomous application bot.

Search results come from web-search indexes and snippets. Always open the original employer/university page and verify:

- deadline
- eligibility
- funding
- salary/stipend
- visa requirements
- application method

The AI must not be treated as proof that an opportunity is currently open.

## 3. Run locally

Install Python 3.10+.

```bash
git clone https://github.com/YOUR_USERNAME/khawar-ai-assistant.git
cd khawar-ai-assistant

python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your Groq API key.

Windows PowerShell:

```powershell
$env:GROQ_API_KEY="YOUR_KEY"
```

Linux/macOS:

```bash
export GROQ_API_KEY="YOUR_KEY"
```

Run:

```bash
streamlit run app.py
```

## 4. Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app.
4. Select your GitHub repository.
5. Main file: `app.py`.
6. Deploy.
7. Open the app's Settings / Secrets.
8. Add:

```toml
GROQ_API_KEY = "YOUR_GROQ_API_KEY"
GROQ_MODEL = "llama-3.3-70b-versatile"
```

Do NOT put your real API key in GitHub.

## 5. Customize your profile

Edit:

```text
data/profile.json
```

Replace the placeholder `base_cv` with your latest CV.

The more accurate the profile, the better the matching and tailoring.

## 6. Repository structure

```text
khawar-ai-assistant/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── secrets.toml.example
├── data/
│   └── profile.json
└── modules/
    ├── __init__.py
    ├── ai.py
    ├── job_search.py
    ├── cv_generator.py
    └── utils.py
```

## 7. V2 roadmap

Planned improvements:

- Official job-board/API connectors
- University-specific scholarship sources
- Better duplicate detection
- Opportunity database
- Automatic deadline tracking
- Email alerts
- Scheduled daily searches
- PDF/DOCX CV export
- Multiple CV versions
- LinkedIn/profile import where technically and legally appropriate
- User accounts
- Premium version
- Monetization
- Application tracker
- Opportunity history
