# Sourcer - Wholesale Assistant

AI-powered app that helps real-estate wholesalers quickly price and pitch deals.

## Quick Start

### Run on macOS/iOS
See **[MACOS_SETUP.md](MACOS_SETUP.md)** for complete instructions.

```bash
# Quick start (on macOS)
./setup_macos.sh
open -a Simulator
flutter run
```

### Run on Web/Linux (Dev Container)
```bash
# Terminal 1: Start backend API
cd backend
npm install
npm start
# Backend runs on http://localhost:3000

# Terminal 2: Build and serve Flutter web app
flutter build web
cd build/web
python3 -m http.server 8080
# App runs on http://localhost:8080
```

## Features

✅ **Auto-Estimator** - Paste Zillow URL → AI estimates repair items (with web scraping)
✅ **MAO Calculation** - Maximum Allowable Offer formula: `MAO = (ARV × Factor) − Repairs − Fee`
✅ **ZIP-Based Repair Estimation** - Auto-generates line-item budgets by market
✅ **Offer Range** - Aggressive/Target/Safe scenarios
✅ **Negotiation Scripts** - AI-generated talking points
✅ **Cross-Platform** - iOS, Android, Web (Flutter + Expo/React Native)
✅ **Backend API** - Express server with Zillow scraping (with graceful fallback)

## Project Structure

```
lib/main.dart                           # Flutter app (complete MVP)
expo-app/                               # React Native/Expo frontend
  ├── App.tsx                          # Main screen
  └── components/AutoEstimator.tsx     # Zillow → repair items
backend/                                # Express API server
  ├── server.js                        # Main API with Zillow scraping
  ├── SCRAPING_GUIDE.md                # Web scraping documentation
  └── package.json                     # Node dependencies
pubspec.yaml                            # Flutter dependencies
ios/                                    # iOS native project (Flutter)
android/                                # Android native project (Flutter)
assets/pricing/                         # ZIP rate data
.github/copilot-instructions.md         # AI agent guidance
```

See **[FLUTTER_README.md](FLUTTER_README.md)** for Flutter development.  
See **[expo-app/README.md](expo-app/README.md)** for Expo/React Native development. 
