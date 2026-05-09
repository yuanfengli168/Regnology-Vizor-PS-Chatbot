# Frontend — Vizor PS Chatbot

React + Vite + TypeScript chat UI.

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Production. Any push to `main` that touches `frontend/` triggers the GitHub Actions deploy. |
| `mvp1-frontend` | Original MVP branch (merged into `main`). Keep for reference. |

**Always branch off `main` for new frontend work**, e.g. `git checkout -b feat/my-feature`.

---

## Local Development

```bash
cd frontend
npm install       # first time only
npm run dev       # dev server at http://localhost:5173 (hot reload)
```

Create a `.env` file from the example before running:

```bash
cp .env.example .env
# Edit VITE_API_URL to point to the running backend
```

---

## Production Build & Local Hosting

The app is served on the local network via `vite preview`. It auto-starts on laptop login via `launchd`.

```bash
npm run build     # compile to dist/
npm run preview   # serve dist/ at http://localhost:4173
```

**Team URL:** `http://192.168.5.48:4173` _(update if the laptop IP changes)_

### launchd service (macOS auto-start)

The service is registered as `com.regnology.vizor-chatbot-frontend`.

```bash
# Check status
launchctl list | grep vizor

# Stop
launchctl unload ~/Library/LaunchAgents/com.regnology.vizor-chatbot-frontend.plist

# Start
launchctl load ~/Library/LaunchAgents/com.regnology.vizor-chatbot-frontend.plist

# Logs
cat /tmp/vizor-frontend.log
cat /tmp/vizor-frontend-error.log
```

The plist file lives at:
`launchd/com.regnology.vizor-chatbot-frontend.plist` (in repo)
`~/Library/LaunchAgents/com.regnology.vizor-chatbot-frontend.plist` (active copy)

The startup script lives at `~/vizor-start-frontend.sh` — do not delete it.

---

## GitHub Actions Deploy (Public Repo)

When the repo is public, every push to `main` touching `frontend/**` auto-deploys to GitHub Pages via `.github/workflows/deploy-frontend.yml`.

**Required one-time GitHub setup:**
1. Repo → Settings → Pages → Source: `gh-pages` branch, `/ (root)`
2. Add a repository variable `VITE_API_URL` (Settings → Variables → Actions)
3. Add a repository secret `VITE_ADMIN_TOKEN` (Settings → Secrets → Actions)

**Live URL:** `https://yuanfengli168.github.io/Regnology-Vizor-PS-Chatbot/`

> When the backend is ready and running locally, set `VITE_API_URL` to the ngrok tunnel URL or local network IP so GitHub Pages can reach it.

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend base URL | `http://192.168.5.48:8000` |
| `VITE_ADMIN_TOKEN` | Token for the Stop Service button | `some-secret-token` |

Never commit `.env` — it is gitignored.
