# 🚀 Deployment Guide - Cloud Hosting

Deploy the Quant Learning Platform to the cloud for easy access by test clients. No local setup required!

## 📋 Overview

**Architecture:**
```
Test Clients
     ↓
Frontend (Vercel/Netlify) → Backend (Render.com) → PostgreSQL (Render)
                                    ↓                      ↓
                              Pinecone Vector DB    OpenAI API
```

**Estimated Time:** 30-45 minutes
**Cost:** $0/month (using free tiers)

---

## Part 1: Deploy Backend to Render.com

### Step 1: Prepare Your Repository

Render deploys directly from GitHub, so ensure your code is pushed:

```bash
cd /Users/imenalsamarai/Documents/projects_MCP/Quants_Learn
git push origin claude/continue-last-session-01LNeGTFChAH1orybXUtPMRz
```

### Step 2: Create Render Account

1. Go to https://render.com/
2. Click **"Get Started"**
3. Sign up with GitHub (recommended for easy deployment)
4. Authorize Render to access your GitHub repositories

### Step 3: Create PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `quant-learning-db`
   - **Database**: `quant_learn`
   - **User**: (auto-generated)
   - **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
   - **Plan**: **Free** (good for testing)
3. Click **"Create Database"**
4. Wait ~2 minutes for provisioning
5. **Copy the "Internal Database URL"** - you'll need this!

### Step 4: Deploy Backend Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `ImenAlSamarai/Quants_Learn`
3. Configure:
   - **Name**: `quant-learning-backend`
   - **Region**: Same as database
   - **Branch**: `claude/continue-last-session-01LNeGTFChAH1orybXUtPMRz`
   - **Root Directory**: `backend`
   - **Runtime**: **Python 3**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 5: Configure Environment Variables

In the "Environment" section, add these variables:

```env
# Database (use Internal Database URL from Step 3)
DATABASE_URL=postgresql://user:password@hostname/quant_learn

# Pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=aws
PINECONE_INDEX_NAME=quant-learning

# OpenAI
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini

# App Settings
APP_NAME=Quant Learning Platform
DEBUG=False
PYTHONUNBUFFERED=1

# Embedding Settings
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
CHUNK_SIZE=500
CHUNK_OVERLAP=50
```

**Important Notes:**
- Use the **Internal Database URL** from your Render PostgreSQL (not external)
- Set `DEBUG=False` for production
- `PYTHONUNBUFFERED=1` ensures logs appear in Render dashboard

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repo
   - Install dependencies (~3-5 minutes)
   - Start the server
3. Monitor the logs for:
   ```
   Database initialized successfully!
   Server starting at http://0.0.0.0:10000
   ```

### Step 7: Initialize Database & Content

Once deployed, you need to initialize the database and index content:

**Option A: Using Render Shell (Recommended)**
1. In your backend service, click **"Shell"** tab
2. Run:
   ```bash
   python -c "from app.models.database import init_db; init_db()"
   cd ..
   python backend/scripts/index_content.py --init-db --content-dir content
   ```

**Option B: Using Local Script with Remote DB**
```bash
# On your local machine, temporarily use Render's database
export DATABASE_URL="postgresql://user:pass@hostname/quant_learn"
cd backend
python -c "from app.models.database import init_db; init_db()"
python scripts/index_content.py --init-db --content-dir ../content
```

### Step 8: Test Backend

Your backend URL will be: `https://quant-learning-backend.onrender.com`

Test it:
```bash
curl https://quant-learning-backend.onrender.com/health
# Should return: {"status":"healthy"}

curl https://quant-learning-backend.onrender.com/
# Should return API info
```

---

## Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Account

1. Go to https://vercel.com/
2. Click **"Sign Up"**
3. Sign up with GitHub
4. Authorize Vercel to access your repositories

### Step 2: Import Project

1. Click **"Add New..."** → **"Project"**
2. Import `ImenAlSamarai/Quants_Learn`
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### Step 3: Configure Environment Variables

Add this single environment variable:

```env
VITE_API_URL=https://quant-learning-backend.onrender.com
```

**Important:** Use your actual Render backend URL from Part 1!

### Step 4: Deploy

1. Click **"Deploy"**
2. Vercel will:
   - Install dependencies (~2 minutes)
   - Build the React app (~1 minute)
   - Deploy to CDN
3. You'll get a URL like: `https://quants-learn.vercel.app`

### Step 5: Update Backend CORS

Now that you have your frontend URL, update the backend CORS settings:

**On Render:**
1. Go to your backend service
2. Go to **"Environment"** tab
3. Add a new environment variable:
   ```env
   ALLOWED_ORIGINS=https://quants-learn.vercel.app
   ```
4. Or update `backend/app/main.py` line 18:
   ```python
   allow_origins=[
       "http://localhost:3000",
       "http://localhost:5173",
       "https://quants-learn.vercel.app"  # Add your Vercel URL
   ],
   ```
5. Commit and push to trigger redeployment

### Step 6: Test Full Stack

1. Visit your Vercel URL: `https://quants-learn.vercel.app`
2. Open browser console (F12)
3. Try:
   - Setting your learning level
   - Clicking a topic
   - Verifying content loads
4. Check for any CORS errors

---

## Part 3: Alternative Frontend (Netlify)

If you prefer Netlify over Vercel:

### Step 1: Create Netlify Account

1. Go to https://www.netlify.com/
2. Sign up with GitHub

### Step 2: Deploy

1. Click **"Add new site"** → **"Import an existing project"**
2. Choose GitHub → Select `ImenAlSamarai/Quants_Learn`
3. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
   - **Environment variables**:
     ```
     VITE_API_URL=https://quant-learning-backend.onrender.com
     ```
4. Click **"Deploy"**

Your site will be at: `https://random-name-123.netlify.app`

You can customize the domain in **Site settings** → **Domain management**.

---

## 🔧 Post-Deployment Configuration

### Custom Domains (Optional)

**Backend (Render):**
1. Buy domain (e.g., Namecheap, Google Domains)
2. In Render: **Settings** → **Custom Domain**
3. Add: `api.yourquantplatform.com`
4. Follow DNS instructions

**Frontend (Vercel/Netlify):**
1. In Vercel/Netlify: **Settings** → **Domains**
2. Add: `www.yourquantplatform.com`
3. Follow DNS instructions

### SSL Certificates

Both Render and Vercel/Netlify provide free SSL automatically!
- ✅ Your sites will be HTTPS by default
- ✅ Certificates auto-renew

### Monitoring

**Render Backend:**
- **Logs**: Click "Logs" tab to see real-time logs
- **Metrics**: View CPU/Memory usage
- **Alerts**: Set up email alerts for crashes

**Vercel Frontend:**
- **Analytics**: View page views, performance
- **Logs**: See deployment and function logs
- **Speed Insights**: Monitor Core Web Vitals

---

## 💰 Cost Breakdown

### Free Tier Limits

**Render (Free Plan):**
- ✅ 750 hours/month (enough for 24/7 if one service)
- ✅ 512 MB RAM
- ✅ **Spins down after 15 min of inactivity** ⚠️
- ✅ 100 GB bandwidth/month
- ⚠️ First request after spin-down takes 30-60 seconds

**PostgreSQL (Free Plan):**
- ✅ 1 GB storage
- ✅ 97 connections
- ✅ Expires after 90 days (can create new one)

**Vercel (Hobby Plan):**
- ✅ Unlimited personal projects
- ✅ 100 GB bandwidth/month
- ✅ Serverless functions included

**Netlify (Free Plan):**
- ✅ 100 GB bandwidth/month
- ✅ 300 build minutes/month

**Total:** **$0/month** for testing!

### Upgrade Paths (If Needed)

If you need better performance:

**Render Starter ($7/month):**
- No spin-down (always on)
- 512 MB RAM
- Priority support

**Render Standard ($25/month):**
- 2 GB RAM
- Better performance
- Auto-scaling

**PostgreSQL Standard ($7/month):**
- 10 GB storage
- Better performance
- 1-year retention

---

## 🎯 Sharing with Test Clients

### Email Template

```
Subject: Quant Learning Platform - Live Demo Ready!

Hi [Name],

Great news! The Quant Learning Platform is now live and ready for testing.
No installation required - just click the link!

🌐 Live Demo: https://quants-learn.vercel.app

📚 Testing Guide:
1. Open the link above
2. Click ⚙️ Settings to set your learning level
3. Explore topics in Linear Algebra, Calculus, Probability, or Statistics
4. Try different learning levels to see adaptive content

⏱️ Note: First topic load may take 30-60 seconds (generating content with AI)
Subsequent loads are instant!

📝 Feedback:
Please test for 30-45 minutes and report any issues or suggestions.

Testing guide: [Link to TESTING_GUIDE.md in repo]

Thank you for helping improve the platform!

Best,
[Your Name]

---
Live URL: https://quants-learn.vercel.app
GitHub: https://github.com/ImenAlSamarai/Quants_Learn
```

### QR Code (Optional)

Generate a QR code for easy mobile access:
1. Go to https://www.qr-code-generator.com/
2. Enter your Vercel URL
3. Download QR code
4. Share in presentations or documents

---

## 🐛 Troubleshooting

### "Site not loading"
- **Check Render logs**: Is backend running?
- **Check Vercel deployment**: Did build succeed?
- **Verify CORS**: Is frontend URL in backend CORS config?

### "Timeout errors"
- **Render free tier**: First request after spin-down takes 30-60s
- **Solution**: Keep backend alive with uptime monitor (see below)
- **Or**: Upgrade to Starter plan ($7/mo)

### "Database connection errors"
- **Check DATABASE_URL**: Should be Internal URL, not External
- **Verify database is running**: Check Render PostgreSQL status
- **Test connection**: Use Render Shell to test

### "Content not loading"
- **Did you index content?**: Run Part 1, Step 7
- **Check Pinecone**: Verify API key and index name
- **Check OpenAI**: Verify API key and credits

---

## 🔄 Keeping Render Free Tier Alive

Render free tier spins down after 15 minutes of inactivity. To keep it alive:

### Option 1: Uptime Monitor (Recommended)

Use a free service like **UptimeRobot**:
1. Sign up at https://uptimerobot.com/
2. Add new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://quant-learning-backend.onrender.com/health`
   - **Interval**: 5 minutes
3. It will ping your backend every 5 minutes, keeping it awake

### Option 2: Cron Job (Advanced)

Set up a GitHub Action to ping your backend:

`.github/workflows/keep-alive.yml`:
```yaml
name: Keep Backend Alive
on:
  schedule:
    - cron: '*/10 * * * *'  # Every 10 minutes
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping backend
        run: curl https://quant-learning-backend.onrender.com/health
```

---

## ✅ Deployment Checklist

Before sharing with clients:

- [ ] Backend deployed to Render
- [ ] PostgreSQL database created
- [ ] Database initialized and content indexed
- [ ] Backend health check returns 200
- [ ] Frontend deployed to Vercel/Netlify
- [ ] CORS configured for frontend URL
- [ ] Environment variables set correctly
- [ ] Tested full workflow (set level → load topic)
- [ ] LaTeX math rendering works
- [ ] Code highlighting works
- [ ] Progress tracking works
- [ ] Optional: Set up uptime monitoring
- [ ] Optional: Configure custom domain

---

## 🎉 Success!

Your Quant Learning Platform is now live and accessible worldwide!

**Next Steps:**
1. Share URL with test clients
2. Monitor Render logs for errors
3. Check Vercel analytics for usage
4. Gather feedback
5. Iterate for v1.1

**Support:**
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Netlify Docs: https://docs.netlify.com/

---

*Deployment Guide for MVP v1.0*
*Last updated: November 2024*
