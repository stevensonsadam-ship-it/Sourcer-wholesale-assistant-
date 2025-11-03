# Running Sourcer on macOS with iPhone Simulator

## Prerequisites

1. **macOS** with macOS 10.14 (Mojave) or later
2. **Xcode** 12.0 or later (from App Store)
3. **Flutter SDK** installed

## Quick Setup

### 1. Install Flutter (if not already installed)

```bash
# Download Flutter SDK
cd ~/development
git clone https://github.com/flutter/flutter.git -b stable

# Add to PATH (add this to ~/.zshrc or ~/.bash_profile)
export PATH="$PATH:$HOME/development/flutter/bin"

# Verify installation
flutter doctor
```

### 2. Install Xcode Command Line Tools

```bash
xcode-select --install
```

### 3. Accept Xcode License

```bash
sudo xcodebuild -license accept
```

### 🎯 On Your macOS Machine

First, you need to get the code on your local Mac. Choose one option:

**Option A: Clone from GitHub (if pushed)**
```bash
git clone https://github.com/stevensonsadam-ship-it/Sourcer-wholesale-assistant-.git
cd Sourcer-wholesale-assistant-
```

**Option B: Copy from dev container**
If you're working in a dev container, sync/copy the folder to your local Mac first.

**Then run these commands in Terminal:**

```bash
# 1. Make sure you're in the project directory
pwd  # Should show: /Users/yourname/.../Sourcer-wholesale-assistant-

# 2. Run setup script (one-time)
./setup_macos.sh

# 3. Open simulator
open -a Simulator

# 4. Run the app
flutter run
```

### Development Commands

While the app is running:
- **`r`** - Hot reload (instant UI updates)
- **`R`** - Hot restart (full app restart)
- **`q`** - Quit the app
- **`h`** - Show all commands

### Build for iOS Device (Physical iPhone)

```bash
# Open Xcode project
open ios/Runner.xcworkspace

# In Xcode:
# 1. Select your development team (Signing & Capabilities)
# 2. Connect your iPhone
# 3. Select your device from the target dropdown
# 4. Click Run button

# Or from command line:
flutter run -d <device-id>
```

## Troubleshooting

### Issue: "No devices found"

```bash
# Check Flutter devices
flutter devices

# Ensure simulator is running
open -a Simulator
```

### Issue: "CocoaPods not installed"

```bash
# Install CocoaPods
sudo gem install cocoapods

# Setup CocoaPods
cd ios
pod install
cd ..
```

### Issue: Xcode version too old

```bash
# Update Xcode from App Store
# Then run:
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch
```

### Issue: Simulator won't launch

```bash
# Kill all simulator processes
killall -9 com.apple.CoreSimulator.CoreSimulatorService

# Restart simulator
open -a Simulator
```

## Project Structure

```
Sourcer-wholesale-assistant-/
├── lib/
│   └── main.dart              # Flutter app entry point
├── ios/                       # iOS native project
│   ├── Runner.xcworkspace     # Open this in Xcode
│   └── Podfile                # CocoaPods dependencies
├── android/                   # Android native project
├── pubspec.yaml               # Flutter dependencies
└── assets/
    └── pricing/
        └── zip_rates.csv      # ZIP pricing data
```

## Features Ready on macOS/iOS

✅ All features from the Flutter app work on iOS:
- MAO calculation with Factor slider (0.55–0.75)
- ZIP-based repair estimation
- Offer range (Aggressive/Target/Safe)
- Repair budget line items (editable)
- Negotiation scripts
- Risk preference slider
- Material Design 3 UI

## Next Steps After Initial Launch

1. **Test on Real Device**: Connect your iPhone and test
2. **Add App Icon**: Replace `ios/Runner/Assets.xcassets/AppIcon.appiconset/`
3. **Update Bundle ID**: Change in Xcode (default: com.sourcer.sourcerWholesaleAssistant)
4. **App Store Preparation**: Configure signing, provisioning, and metadata

## Performance Tips

- Use **Release mode** for performance testing: `flutter run --release`
- Profile with Xcode Instruments for optimization
- Test on actual device, not just simulator

## Resources

- [Flutter iOS Setup](https://docs.flutter.dev/get-started/install/macos)
- [Xcode Documentation](https://developer.apple.com/xcode/)
- [Flutter DevTools](https://docs.flutter.dev/tools/devtools/overview)
