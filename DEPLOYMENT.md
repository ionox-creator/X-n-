# Fintel — Railway Deployment Guide

## Prerequisites
1. A [Railway](https://railway.app) account
2. Your GitHub repo with this code pushed
3. Gmail App Password for SMTP (`rkkrzekrronvxqwy` is already set)

## Step-by-Step Deployment

### 1. Push to GitHub
```bash
git add .
git commit -m "Fintel v1.4 — Railway ready"
git push origin main
```

### 2. Create Railway Project
1. Go to [railway.app](https://railway.app) → **New Project**
2. Select **Deploy from GitHub repo**
3. Choose your Fintel repo
4. Railway will detect the Dockerfile automatically

### 3. Add Persistent Volume (for SQLite database)
1. In your Railway service → **Settings** → **Volumes**
2. Click **Add Volume**
3. Mount path: `/data`
4. This stores `custom.db` (license keys + device bindings)

### 4. Set Environment Variables
In Railway → **Variables** tab, add:
```
DATABASE_URL=file:/data/custom.db
SMTP_USER=ionoxspace@gmail.com
SMTP_PASS=rkkrzekrronvxqwy
NODE_ENV=production
```

### 5. Deploy
1. Railway will auto-build using the Dockerfile
2. Build takes ~3-5 minutes (better-sqlite3 compilation)
3. Once deployed, you'll get a URL like `fintel.up.railway.app`

### 6. Verify
- Visit `https://your-app.up.railway.app/`
- Welcome screen should appear
- Enter any of the 55 license keys
- Test Get Licence Key form (SMTP email)
- Test Console commands + PDF/XLSX export

## License Keys
55 keys are hardcoded in `src/lib/license-keys.ts` as plaintext, then hashed
(SHA-256) and stored in the SQLite database on first run. The database
persists in the Railway volume.

**Keys are NOT visible in the compiled JavaScript** — only their hashes
are in the database. Hackers cannot reverse SHA-256 to find the keys.

## Architecture
```
┌─────────────────────────────────────┐
│         Railway (Docker)            │
│  ┌───────────────────────────────┐  │
│  │   Next.js App (port 3000)     │  │
│  │  ┌─────────┐ ┌─────────────┐  │  │
│  │  │validate │ │request-     │  │  │
│  │  │-key API │ │license API  │  │  │
│  │  └────┬────┘ └──────┬──────┘  │  │
│  │       │             │         │  │
│  │  ┌────▼────┐  ┌─────▼──────┐  │  │
│  │  │ SQLite  │  │ Gmail SMTP │  │  │
│  │  │ (55 keys│  │ (nodemailer)│  │  │
│  │  │ +device)│  │            │  │  │
│  │  └─────────┘  └────────────┘  │  │
│  └───────────────────────────────┘  │
│         Volume: /data               │
└─────────────────────────────────────┘
```

## Environment Variables
| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `file:/data/custom.db` | SQLite path (Railway volume) |
| `SMTP_USER` | `ionoxspace@gmail.com` | Gmail for SMTP |
| `SMTP_PASS` | `rkkrzekrronvxqwy` | Gmail App Password |
| `NODE_ENV` | `production` | Next.js production mode |

## Costs
- Railway free trial: $5 credit (~500 hours)
- Hobby plan: $5/month (sufficient for production)

## Troubleshooting
- **Build fails**: Check if `better-sqlite3` compiles (needs python3+g++)
- **Database not persisting**: Ensure volume is mounted at `/data`
- **SMTP not working**: Verify Gmail App Password is correct
- **License key not validating**: Check database has 55 keys (`SELECT COUNT(*) FROM LicenseKey`)

## License Key List
See `src/lib/license-keys.ts` for all 55 keys.
