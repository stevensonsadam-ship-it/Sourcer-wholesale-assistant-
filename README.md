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
flutter pub get
flutter run -d web-server --web-port=8080
# Open http://localhost:8080
```

## Features

✅ **MAO Calculation** - Maximum Allowable Offer formula: `MAO = (ARV × Factor) − Repairs − Fee`
✅ **ZIP-Based Repair Estimation** - Auto-generates line-item budgets by market
✅ **Offer Range** - Aggressive/Target/Safe scenarios
✅ **Negotiation Scripts** - AI-generated talking points
✅ **Cross-Platform** - iOS, Android, Web

## Project Structure

```
lib/main.dart              # Flutter app (complete MVP)
pubspec.yaml               # Dependencies
ios/                       # iOS native project
android/                   # Android native project
assets/pricing/            # ZIP rate data
.github/copilot-instructions.md  # AI agent guidance
```

See **[FLUTTER_README.md](FLUTTER_README.md)** for development details. 
