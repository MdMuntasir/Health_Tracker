# Health Tracker API

A REST API for tracking personal health data — workouts, nutrition, body metrics, goals, and reminders — with AI-powered recommendations via Google Gemini.

**Live:** https://4n6s34wjkxz643aru7v3wvdur40jqfbl.lambda-url.ap-south-1.on.aws/

## Stack

- **FastAPI** — API framework
- **AWS Lambda + DynamoDB** — serverless compute and storage
- **Google Gemini** — AI health recommendations
- **JWT** — authentication

## Endpoints

| Prefix | Description |
|---|---|
| `/auth` | Register and login |
| `/workouts` | Log and retrieve workouts |
| `/nutrition` | Nutrition and water intake |
| `/metrics` | Body metrics (weight, BMI, sleep, steps) |
| `/goals` | Goal setting and progress |
| `/reminders` | Health reminders |
| `/reports` | Analytics and reports |
| `/ai` | AI-generated workout plans, diet tips, and insights |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your credentials
uvicorn app.main:app --reload
```

Docs available at `/docs` (Swagger) and `/redoc`.

## Environment Variables

See `.env.example` for required variables (AWS credentials, JWT secret, Gemini API key).
