# Vercel Deployment Fix

## What Was Fixed:

### 1. **Updated vercel.json Configuration**
- Changed `routes` to `rewrites` (new Vercel format)
- Changed `dest` to `destination`
- Removed deprecated `version: 2`
- Fixed SPA routing to properly serve index.html for all routes

### 2. **Added Root-Level vercel.json**
- Tells Vercel the project is in `expo-app/` directory
- Specifies correct `outputDirectory: expo-app/dist`
- Sets proper build commands

### 3. **Added .vercelignore**
- Excludes unnecessary files (backend, android, ios, etc.)
- Speeds up deployment by reducing upload size

---

## Deploy to Vercel Now:

### Option 1: Vercel Dashboard (Recommended)

1. **Go to:** https://vercel.com
2. **Click:** "Add New..." → "Project"
3. **Import your repo:** `stevensonsadam-ship-it/Sourcer-wholesale-assistant-`
4. **Configure:**
   - Framework Preset: **Other**
   - Root Directory: **Leave as root** (vercel.json handles it)
   - Build Command: **Leave default** (uses vercel.json)
   - Output Directory: **Leave default** (uses vercel.json)
5. **Environment Variables** (optional):
   - `EXPO_PUBLIC_API_BASE` = `https://your-backend-url.com` (when you deploy backend)
6. **Click:** "Deploy"

### Option 2: Vercel CLI (If authentication works)

```bash
cd /workspaces/Sourcer-wholesale-assistant-
vercel --prod
```

---

## After Deployment:

Your app will be live at: `https://your-project.vercel.app`

### Test These Features:
- ✅ Homepage loads (not 404)
- ✅ All routes work (SPA routing)
- ✅ Static assets load (_expo/static/js/...)
- ✅ Deal input form works
- ✅ Offer calculations display
- ✅ Negotiation scripts render

---

## What Fixed the 404:

**Before:**
- Vercel couldn't find files because it was looking in the wrong directory
- Old routing configuration didn't properly handle SPA routes

**After:**
- Root `vercel.json` tells Vercel to build from `expo-app/`
- New `rewrites` configuration properly handles all routes → index.html
- `.vercelignore` speeds up deployment by excluding 100MB+ of unnecessary files

---

## Next Steps:

1. **Deploy frontend** (this fix)
2. **Deploy backend** to Render/Railway (for Zillow scraping)
3. **Add environment variable** on Vercel for `EXPO_PUBLIC_API_BASE`
4. **Test live app** with real Zillow URLs

---

## Troubleshooting:

If 404 still appears:
1. Check Vercel deployment logs
2. Verify `expo-app/dist/index.html` exists
3. Ensure build succeeded
4. Try manual redeploy from Vercel dashboard

Your deployment should work now! 🚀
