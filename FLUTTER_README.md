# Sourcer - Wholesale Assistant (Flutter)

AI-powered app that helps real-estate wholesalers quickly price and pitch deals.

## Features Implemented

✅ **MAO Calculation** - Maximum Allowable Offer using formula: `MAO = (ARV × Factor) − Repairs − Fee`
- Adjustable Factor slider (0.55–0.75, default 0.65)
- Three offer scenarios: Aggressive, Target, Safe

✅ **ZIP-Based Repair Estimation** - Auto-generates line-item repair budgets
- Houston area (770xx): 0.9x multiplier, ~35 DOM
- Los Angeles area (900xx): 1.25x multiplier, ~42 DOM
- National default: 1.0x multiplier, ~30 DOM
- Editable line items with trade, qty, unit cost, total

✅ **Risk Preference Slider** - Adjusts recommended offer between safe and aggressive

✅ **Negotiation Scripts** - Auto-generated talking points based on deal numbers

✅ **UI Components**
- Deal input (URL, address, ZIP, ARV, fee)
- Offer range cards (color-coded)
- Repair budget table (editable)
- Market signals display
- Save to pipeline (stub)
- PDF/Share export (stub)

## Quick Start

### Prerequisites

Install Flutter SDK: https://docs.flutter.dev/get-started/install

### Run the App

```bash
# Install dependencies
flutter pub get

# Run on Chrome (web)
flutter run -d chrome

# Run on connected device/emulator
flutter run

# For hot-reload: press 'r' in terminal or save files in IDE
```

### Development

- **Hot reload**: Press `r` in terminal or save files
- **Hot restart**: Press `R` in terminal
- **Quit**: Press `q` in terminal

### Project Structure

```
lib/
  main.dart          # Complete Sourcer app (single-file for MVP)
pubspec.yaml         # Flutter dependencies
```

## Next Steps

- [ ] Connect to real listing APIs (Zillow, Realtor.com)
- [ ] Add Supabase/Firebase backend for deal pipeline
- [ ] Implement PDF generation (pdf package)
- [ ] Add SMS/text export (Twilio integration)
- [ ] Create comp analysis screen with adjustments table
- [ ] Add CRM webhook integrations (Zapier, REsimpli, Podio)
- [ ] Split into multi-file architecture (models/, screens/, services/)

## MAO Formula Reference

```dart
MAO = (ARV × Factor) − Repairs − Assignment Fee

// Default values
Factor: 0.65 (range: 0.55–0.75)
Assignment Fee: $5,000 (user-configurable)
Repairs: Auto-estimated by ZIP code
```

## Architecture Notes

See `.github/copilot-instructions.md` for AI agent guidance on this codebase.

Current implementation is single-file MVP. When scaling:
- Extract models to `lib/models/`
- Extract screens to `lib/screens/`
- Add services layer for API calls (`lib/services/`)
- Add state management (Provider, Riverpod, or Bloc)
