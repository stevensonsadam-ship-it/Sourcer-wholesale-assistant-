# Sourcer - Production Deployment Guide

## 🚀 Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Set `EXPO_PUBLIC_API_BASE` to production API URL
- [ ] Configure backend API endpoints for auto-estimation
- [ ] Set up analytics/monitoring (optional)
- [ ] Configure error tracking (Sentry, etc.)

### 2. App Configuration (`app.json`)
- [x] Bundle identifier: `com.sourcer.wholesale`
- [x] App name: "Sourcer"
- [ ] Update version number before each release
- [ ] Add app icons (icon.png, adaptive-icon.png, favicon.png)
- [ ] Configure app store metadata

### 3. Code Quality
- [x] All TypeScript errors resolved
- [x] No console.log/debug statements in production
- [x] All features tested across platforms
- [x] Responsive design verified

---

## 📱 Platform-Specific Builds

### **Web (Static Export)**

#### Development Server
```bash
cd expo-app
npm run web
# Runs at http://localhost:8081
```

#### Production Build
```bash
# Build static web app
npx expo export:web

# Output in: web-build/
# Deploy to: Vercel, Netlify, AWS S3 + CloudFront, etc.
```

#### Deploy to Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd expo-app
vercel --prod

# Or use Vercel GitHub integration (auto-deploy on push)
```

#### Deploy to Netlify
```bash
# Build first
npx expo export:web

# Deploy web-build/ folder via Netlify CLI or drag-and-drop
netlify deploy --prod --dir=web-build
```

---

### **iOS (App Store)**

#### Prerequisites
- macOS with Xcode 14+
- Apple Developer account ($99/year)
- EAS CLI: `npm install -g eas-cli`

#### Build with EAS (Recommended)
```bash
# Login to Expo
eas login

# Configure project
eas build:configure

# Build for iOS
eas build --platform ios --profile production

# Submit to App Store
eas submit --platform ios
```

#### Local Build (Alternative)
```bash
# Generate native iOS project
npx expo prebuild --platform ios

# Open in Xcode
open ios/SourcerWholesaleAssistant.xcworkspace

# Archive and submit via Xcode
```

---

### **Android (Google Play)**

#### Prerequisites
- Android Studio
- Google Play Developer account ($25 one-time)
- Java keystore for app signing

#### Build with EAS (Recommended)
```bash
# Build for Android
eas build --platform android --profile production

# Submit to Google Play
eas submit --platform android
```

#### Local Build (Alternative)
```bash
# Generate native Android project
npx expo prebuild --platform android

# Build APK/AAB
cd android
./gradlew assembleRelease
# or
./gradlew bundleRelease

# Output: android/app/build/outputs/
```

---

## 🔧 Backend Requirements

### Required API Endpoint
The app expects a backend API for auto-estimation:

**Endpoint:** `POST /api/estimateFromZillow`

**Request:**
```json
{
  "url": "https://www.zillow.com/...",
  "sqft": 1500,
  "zipcode": "77033",
  "dealId": "deal_1234567890"
}
```

**Response:**
```json
{
  "items": [
    {
      "key": "interior_paint",
      "label": "Interior paint",
      "amount": 1800,
      "confidence": 0.85
    }
  ]
}
```

### Backend Setup Options
1. **Node.js/Express** - See `backend/server.js` in repo
2. **Python/FastAPI** - See `lib/sintrix_wholesale_estimator/` in repo
3. **Serverless** - Deploy as AWS Lambda, Vercel Functions, etc.

---

## 🌐 Environment Variables

Create `.env` file in `expo-app/`:

```bash
# API Configuration
EXPO_PUBLIC_API_BASE=https://api.yourdomain.com

# Optional: Analytics
EXPO_PUBLIC_ANALYTICS_KEY=your_key_here

# Optional: Error Tracking
EXPO_PUBLIC_SENTRY_DSN=your_dsn_here
```

**Important:** 
- Variables prefixed with `EXPO_PUBLIC_` are embedded in the client
- Never store secrets in these variables
- Use server-side API keys for sensitive operations

---

## 📦 Production Build Commands

Add to `package.json` scripts:

```json
{
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "build:web": "expo export:web",
    "build:ios": "eas build --platform ios --profile production",
    "build:android": "eas build --platform android --profile production",
    "deploy:web": "vercel --prod"
  }
}
```

---

## 🧪 Testing Before Production

### Manual Testing Checklist
- [ ] Test auto-estimate with real Zillow URLs
- [ ] Verify MAO calculations with various inputs
- [ ] Test Factor slider (0.55 - 0.75 range)
- [ ] Test Risk slider (Safe/Balanced/Aggressive)
- [ ] Edit repair items (add, remove, modify)
- [ ] Switch between all 5 negotiation script modes
- [ ] Test PDF/Share functionality
- [ ] Verify all offer calculations update live
- [ ] Test on mobile viewport (responsive design)

### Cross-Platform Testing
- [ ] iOS Safari (if deploying iOS app)
- [ ] Android Chrome (if deploying Android app)
- [ ] Desktop Chrome, Firefox, Safari
- [ ] Tablet/iPad view

---

## 📊 Post-Deployment Monitoring

### Key Metrics to Track
- User engagement with auto-estimate feature
- Most-used negotiation script modes
- Average deal values (ARV, repairs, offers)
- Conversion: estimates → saved deals
- Platform usage (iOS vs Android vs Web)

### Recommended Tools
- **Analytics:** Google Analytics, Mixpanel, Amplitude
- **Error Tracking:** Sentry, Bugsnag
- **Performance:** Vercel Analytics, Lighthouse CI
- **User Feedback:** Intercom, HelpScout

---

## 🔐 Security Considerations

### Client-Side (Current Implementation)
- ✅ No sensitive data stored in app
- ✅ All calculations done client-side (no PII sent to server)
- ⚠️ API endpoint for auto-estimate should be rate-limited

### Recommended Enhancements
- Add authentication (Firebase Auth, Auth0, Clerk)
- Implement user accounts for deal pipeline persistence
- Add server-side validation for all inputs
- Rate limit API requests per IP/user
- HTTPS only (enforce in production)

---

## 🚦 Deployment Workflow

### Recommended Git Flow
```bash
# Development
git checkout -b feature/new-feature
# ... make changes ...
git commit -m "Add new feature"
git push origin feature/new-feature

# Pull request → main
# CI/CD auto-deploys to staging

# Production release
git tag v1.0.0
git push origin v1.0.0
# CI/CD auto-deploys to production
```

### Vercel GitHub Integration (Web)
1. Connect GitHub repo to Vercel
2. Set `expo-app` as root directory
3. Build command: `npx expo export:web`
4. Output directory: `web-build`
5. Environment variables → add `EXPO_PUBLIC_API_BASE`

### EAS Build (Mobile)
1. Configure `eas.json` (already in repo)
2. Set up profiles: development, preview, production
3. Connect to Apple/Google accounts
4. Run `eas build` and `eas submit`

---

## 📝 Version Management

### Semantic Versioning
- **Major (1.0.0):** Breaking changes
- **Minor (1.1.0):** New features, backward compatible
- **Patch (1.0.1):** Bug fixes

### Update `app.json` Before Each Release
```json
{
  "expo": {
    "version": "1.0.0",
    "ios": {
      "buildNumber": "1"
    },
    "android": {
      "versionCode": 1
    }
  }
}
```

---

## 🆘 Troubleshooting

### "Module not found" errors
```bash
npm install
npx expo start -c  # clear cache
```

### Web build fails
```bash
rm -rf web-build node_modules
npm install
npx expo export:web
```

### iOS build fails
- Check Xcode version (must be 14+)
- Update CocoaPods: `cd ios && pod install`
- Clear derived data in Xcode

### Android build fails
- Check Java version (must be 17)
- Clean: `cd android && ./gradlew clean`
- Rebuild: `./gradlew assembleRelease`

---

## 🎯 Launch Checklist

### Pre-Launch
- [ ] All features tested end-to-end
- [ ] Backend API deployed and tested
- [ ] Environment variables configured
- [ ] App icons and splash screens added
- [ ] App store listings prepared (screenshots, descriptions)
- [ ] Privacy policy and terms of service ready
- [ ] Support email/contact configured

### Launch Day
- [ ] Deploy backend first (verify endpoints)
- [ ] Deploy web app (test live URL)
- [ ] Submit mobile apps for review (if applicable)
- [ ] Monitor error tracking dashboard
- [ ] Prepare customer support channels

### Post-Launch
- [ ] Monitor analytics for first 24-48 hours
- [ ] Address critical bugs immediately
- [ ] Collect user feedback
- [ ] Plan iteration based on usage data

---

## 📧 Support

For deployment issues or questions:
- Open issue in GitHub repo
- Contact: [your-email@domain.com]
- Documentation: [your-docs-url]

---

**Congratulations on launching Sourcer! 🎉**

Remember:
- Start with web deployment (fastest)
- Mobile app review takes 1-7 days
- Iterate based on real user feedback
- Keep the MAO formula accurate and transparent
