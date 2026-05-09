# DRO Deployment Guide

## Prerequisites

- Git installed
- GitHub account
- [Render](https://render.com) account (free tier works)

---

## Step 1: Initialize Git & Push to GitHub

```bash
cd C:\Users\DELL\Desktop\dro

# Initialize git
git init
git add -A
git commit -m "Initial commit: DRO Agentic Commerce Engine v2.0"

# Create repo on GitHub (via browser or CLI)
# Then:
git remote add origin https://github.com/YOUR_USERNAME/dro.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy API Service on Render

1. Log into [Render Dashboard](https://dashboard.render.com)
2. Click **"New +" → "Web Service"**
3. Connect your GitHub repo (`dro`)
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `dro-api` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app.routes_api:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile -` |
| **Plan** | Free |

5. Add Environment Variables:

| Key | Value | Description |
|-----|-------|-------------|
| `PYTHON_VERSION` | `3.11.0` | Python runtime version |
| `DEBUG` | `false` | Disable debug mode |
| `DRO_LICENSE_SECRET` | *(choose a random string)* | License signing key |
| `DRO_LICENSE_SALT` | *(choose a random string)* | License encryption salt |
| `OPENAI_API_KEY` | *(optional)* | Your OpenAI API key |
| `CLAUDE_API_KEY` | *(optional)* | Your Claude API key |

6. Click **"Create Web Service"**

Render will build and deploy. After ~3 minutes you'll get:
- **Public URL**: `https://dro-api.onrender.com`
- **API Docs**: `https://dro-api.onrender.com/docs`
- **Health Check**: `https://dro-api.onrender.com/api/health`

---

## Step 3: Deploy Dashboard Service on Render

1. In Render dashboard, click **"New +" → "Web Service"**
2. Connect the same GitHub repo
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `dro-dashboard` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app/dashboard.py --server.port=$PORT --server.headless=true --browser.gatherUsageStats=false` |
| **Plan** | Free |

4. Add Environment Variables:

| Key | Value | Description |
|-----|-------|-------------|
| `PYTHON_VERSION` | `3.11.0` | Python runtime version |
| `DRO_API_URL` | `https://dro-api.onrender.com` | API server URL (no trailing slash) |

5. Click **"Create Web Service"**

After ~3 minutes you'll get:
- **Public URL**: `https://dro-dashboard.onrender.com`

---

## Step 4: Verify Deployment

```bash
# Test API health
curl https://dro-api.onrender.com/api/health

# Expected response:
# {"status":"healthy","ai_service":"mock","licensed":false,"modules":["research","store","copywriting","images","ads","campaign"]}

# Test root
curl https://dro-api.onrender.com/

# Open dashboard in browser
# https://dro-dashboard.onrender.com
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | No | - | OpenAI GPT-4 API key |
| `CLAUDE_API_KEY` | No | - | Claude API key |
| `DRO_LICENSE_KEY` | No | - | License key for production |
| `DRO_LICENSE_SECRET` | No | built-in | License signing secret (change for production) |
| `DRO_LICENSE_SALT` | No | built-in | License encryption salt (change for production) |
| `HOST` | No | `0.0.0.0` | Server bind address |
| `PORT` | No | `8000` | API server port |
| `DEBUG` | No | `false` | Enable debug / bypass license |
| `DRO_API_URL` | Yes* | `http://localhost:8000` | Dashboard API endpoint (*required for dashboard) |
| `WEB_CONCURRENCY` | No | `2` | Gunicorn worker count |

---

## Updating

```bash
# Make changes, then:
git add -A
git commit -m "Update description"
git push

# Render auto-deploys on push to main branch.
```

## Troubleshooting

- **Dashboard shows "Connection error"**: Ensure `DRO_API_URL` points to your API service URL
- **License errors**: Generate a license key with `python main.py license-gen` on the server, or set `DEBUG=true` during development
- **Module not found**: Verify `requirements.txt` is up to date, check build logs in Render dashboard
- **Free tier sleep**: Render free services spin down after 15 min of inactivity; first request after idle takes ~30s to wake up

## Alternative: Heroku (Legacy)

```bash
# Procfile is already configured. To deploy to Heroku:
heroku create dro-app
heroku config:set PYTHON_RUNTIME_VERSION=3.11.0
git push heroku main
```
