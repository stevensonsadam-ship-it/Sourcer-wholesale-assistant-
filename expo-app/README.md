# Sourcer - Wholesale Real Estate Deal Assistant

AI-powered wholesale assistant for real-estate deal analysis and offer generation.

## 🚀 Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/stevensonsadam-ship-it/Sourcer-wholesale-assistant-&project-name=sourcer&repository-name=sourcer&root-directory=expo-app)

**Manual Deploy:**
```bash
npm i -g vercel
cd expo-app
vercel --prod
```

## Features

✅ **Auto-Estimator** - Paste Zillow URL, get AI-estimated repair items
✅ **MAO Calculation** - Real-time offer calculations (Aggressive/Target/Safe)
✅ **ZIP-Based Pricing** - Automatic regional cost adjustments
✅ **Repair Budget** - Customizable line-item breakdown
✅ **5 Negotiation Scripts** - Standard, Friendly, Firm, Agent, Follow-up
✅ **Cross-Platform** - iOS, Android, Web

## Quick Start

### Prerequisites
- Node.js 18+ and npm/yarn
- Expo CLI: `npm install -g expo-cli`
- For iOS: Xcode on macOS
- For Android: Android Studio

### Installation

```bash
cd expo-app
npm install
```

### Run Development Server

```bash
# Start Expo dev server
npm start

# Run on iOS simulator
npm run ios

# Run on Android emulator
npm run android

# Run in web browser
npm run web
```

### Environment Variables

Create `.env` file:

```bash
EXPO_PUBLIC_API_BASE=http://localhost:3000
# or your production API endpoint
```

## Project Structure

```
expo-app/
├── App.tsx                      # Main app screen
├── components/
│   └── AutoEstimator.tsx        # Zillow URL → repair items
├── app.json                     # Expo configuration
├── package.json                 # Dependencies
└── .env                         # Environment variables
```

## Backend Integration

The `AutoEstimator` component expects a backend endpoint:

**POST** `/api/estimateFromZillow`

Request:
```json
{
  "url": "https://zillow.com/...",
  "sqft": 1500,
  "zipcode": "77033",
  "dealId": "deal_123"
}
```

Response:
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

## Components

### AutoEstimator

Fetches AI-estimated repair items from Zillow listing URL.

```tsx
<AutoEstimator
  dealId="deal_123"
  sqft={1500}
  zipcode="77033"
  onApply={(items) => setRepairItems(items)}
/>
```

### Props
- `dealId` - Unique deal identifier
- `sqft` - Property square footage
- `zipcode` - Property ZIP code
- `onApply` - Callback when items are fetched

## MAO Formula

```
MAO = (ARV × Factor) − Repairs − Assignment Fee
```

- **Factor**: 0.55–0.75 (default 0.65)
- **ARV**: After Repair Value
- **Repairs**: Sum of all repair line items
- **Assignment Fee**: User-configurable

## Deployment

### iOS App Store

```bash
eas build --platform ios
eas submit --platform ios
```

### Google Play Store

```bash
eas build --platform android
eas submit --platform android
```

### Web

```bash
npx expo export:web
# Deploy build/ folder to hosting (Vercel, Netlify, etc)
```

## Next Steps

- [ ] Connect to backend API (FastAPI/Express)
- [ ] Add authentication (Supabase/Firebase)
- [ ] Implement deal pipeline storage
- [ ] Add PDF export with `react-native-pdf`
- [ ] Integrate SMS sharing with Twilio
- [ ] Add camera for property photos
- [ ] Implement offline mode with AsyncStorage

## Resources

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Docs](https://reactnative.dev/)
- [Expo Router](https://docs.expo.dev/router/introduction/)
