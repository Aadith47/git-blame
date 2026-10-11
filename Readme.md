# GitHub Analyser

Enter a GitHub username. The app reads the public data, scores the profile out of 100 with plain
Python, and then asks an LLM to explain the result: strengths, weaknesses, recommendations and an
action plan.

Python works out the facts. The LLM only explains them. It never calculates the score.

## Features

- Profile and repository data from the GitHub API (PyGithub)
- A transparent 0-100 score with a breakdown for every category
- Interactive Plotly charts
- The AI review comes back as a typed object (Pydantic), not free text
- Gemini writes the review. OpenAI is an optional backup if Gemini fails
- If every LLM fails, the score and the charts still show
- Forked repositories are left out of every number. Only your own work counts

## How it works

```
username
   |
   v
GitHub API --> cache --> pandas --> Facts          (one fork-free set of numbers)
                                      |
                       LangGraph      v
                    +----------- scoring ----------+
                    |            (plain Python)    |
                    |                              |
            own repos found?                  no own repos
                    |                              |
                    v                              v
                 review                          (skip)
        Gemini, then OpenAI as backup              |
                    |                              |
                    +--------------+---------------+
                                   v
                           Streamlit dashboard
```

## Project structure

```
github-analyser/
├── app.py                     Streamlit app
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
├── github_analyser/
│   ├── config.py              settings from .env (pydantic-settings)
│   ├── models.py              Profile and Repo dataclasses
│   ├── github_client.py       reads GitHub through PyGithub
│   ├── analytics.py           pandas: repos in, Facts out
│   ├── scoring.py             the 0-100 score
│   ├── charts.py              Plotly figures
│   ├── schemas.py             the shape of the AI review
│   ├── llm.py                 Gemini + OpenAI backup (LangChain)
│   └── workflow.py            the LangGraph pipeline
└── tests/
```

## Setup

You need Python 3.10 or newer. Run these in the project folder.

```bash
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # macOS/Linux: cp .env.example .env
```

Open `.env` and fill in your keys.

| Variable | Required | What it is |
|---|---|---|
| `GITHUB_TOKEN` | yes | GitHub personal access token. Read-only is enough. Without one you get 60 requests per hour. |
| `GEMINI_API_KEY` | yes | Google AI Studio key |
| `OPENAI_API_KEY` | no | Backup LLM. Used only if Gemini fails |

## Run

```bash
streamlit run app.py
```

## Tests

```bash
pytest
```

The tests need no network and no API keys.

## Scoring

Forks are left out of every category. Stars and followers are log-scaled, so going from 0 to
10 stars matters more than going from 100 to 110.

| Category | Points | How |
|---|---|---|
| Profile quality | 15 | Bio (5), location or company (4), account age (6, full marks at one year) |
| Repository quality | 25 | Three equal parts: average stars per repo, topics and license, recent pushes with few open issues |
| Documentation | 20 | Share of repos with a README (70%) and with a description (30%) |
| Project diversity | 15 | Languages used. Full marks at 3, one language earns a third |
| Activity | 15 | Share of repos pushed to in the last 90 days (40%) and last year (60%) |
| Community | 10 | Followers (50%) and stars plus forks on your own repos (50%) |

## Notes

- Only the 100 most recently pushed repos are read, and README checks are limited to the 30 most
  recent own repos. Each check is one extra API call. Repos that were not checked are left out
  of the README ratio. They are not counted as missing.
- Activity uses the last push date, not the "updated" date, because "updated" also changes when
  settings change.
- The scoring weights are a starting point. They have not been tested against real data.
- Model names are two constants at the top of `github_analyser/llm.py`. Model names change often.
- GitHub data is cached for one hour. Tick "Skip the cache" to force fresh data.