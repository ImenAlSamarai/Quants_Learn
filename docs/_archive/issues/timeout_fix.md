# Timeout Configuration Fix

## Problem

Users were experiencing "❌ Failed to generate learning path" errors after about 1 minute, even though the backend was successfully completing the learning path generation 2-5 minutes later.

## Root Cause

The Vite development server proxy was using the default Node.js HTTP timeout (~120 seconds / 2 minutes), causing requests to timeout before the backend finished processing.

**Processing time breakdown:**
```
1. Job analysis (GPT-4o-mini)           ~5-10s
2. Topic extraction                     ~5-10s
3. Coverage checking (13 topics avg)    ~10-20s per topic = 2-4 minutes
4. RAG retrieval (books + web)          ~5-10s per topic
5. Topic structure generation           ~2-3s per topic

Total: 1-5 minutes depending on complexity
```

## Solution

### Frontend Changes

**1. Increased axios timeout** (`frontend/src/services/api.js`)
```javascript
// Before: 300000 (5 minutes)
// After:  600000 (10 minutes)
timeout: 600000,
```

**2. Added Vite proxy timeouts** (`frontend/vite.config.js`)
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    timeout: 600000,       // NEW: 10 minute timeout
    proxyTimeout: 600000,  // NEW: 10 minute proxy timeout
  }
}
```

## Why This Fixes It

The issue was the **Vite proxy timeout**, not the axios timeout:

```
Frontend → axios (10min timeout) → Vite proxy (NO TIMEOUT SET) → Backend
                                        ↑
                                This was timing out at ~2 min
```

Even though axios had a 5 minute timeout, the Vite proxy was timing out first using Node.js defaults (~2 minutes).

Now:
```
Frontend → axios (10min) → Vite proxy (10min) → Backend (no timeout)
                              ↑
                        Now properly configured
```

## Testing

After this fix, users should see:

1. **Button shows "Generating Path..."** - immediate feedback
2. **No timeout errors** - even for complex job descriptions
3. **Success after 1-5 minutes** - learning path displayed

## For Production Deployment

If deploying behind nginx or another reverse proxy, make sure to configure timeouts:

### Nginx Configuration
```nginx
location /api {
    proxy_pass http://backend:8000;
    proxy_read_timeout 600s;    # 10 minutes
    proxy_connect_timeout 60s;  # 1 minute
    proxy_send_timeout 600s;    # 10 minutes
}
```

### Docker Compose
```yaml
services:
  nginx:
    environment:
      - PROXY_READ_TIMEOUT=600s
      - PROXY_CONNECT_TIMEOUT=60s
```

## Timeout Hierarchy

**Current configuration:**

| Layer | Timeout | Purpose |
|-------|---------|---------|
| Frontend Axios | 10 min | HTTP request timeout |
| Vite Proxy | 10 min | Dev server proxy timeout |
| Backend FastAPI | None | No timeout (processes until done) |
| Individual LLM calls | 60s | OpenAI client timeout (per call) |

**Important:** The OpenAI client timeout (60s) is per API call, not for the entire endpoint. Learning path generation makes multiple sequential LLM calls, so the total time can be several minutes.

## Monitoring Generation Time

To see how long generation actually takes:

```bash
cd backend
python main.py

# Watch the console output:
📥 USER INPUT RECEIVED (timestamp)
🔍 Analyzing job description... (~10s)
📊 COVERAGE ANALYSIS COMPLETE (~2-4 min)
✓ Learning path generated (timestamp)
```

Typical times:
- Simple job (5 topics): ~1-2 minutes
- Average job (10 topics): ~2-3 minutes
- Complex job (15+ topics): ~3-5 minutes

## Related Files

- `frontend/src/services/api.js` - Axios timeout configuration
- `frontend/vite.config.js` - Vite proxy timeout configuration
- `backend/app/main.py` - Backend server configuration (no timeout)
- `backend/app/services/vector_store.py` - OpenAI client timeout (60s per call)

## Commit

**Commit:** `99f3a2c` - Fix timeout issue for learning path generation

---

**Status:** ✅ Fixed - Frontend now waits 10 minutes for learning path generation
