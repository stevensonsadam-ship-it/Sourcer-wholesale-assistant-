# 🚀 Quick Reference - Running on macOS

## One-Time Setup (5 minutes)

**First, get the code on your Mac:**
```bash
# Clone from GitHub (replace with your actual repo URL)
git clone https://github.com/stevensonsadam-ship-it/Sourcer-wholesale-assistant-.git
cd Sourcer-wholesale-assistant-

# OR if you already have the code, just cd into it:
cd ~/path/where/you/have/Sourcer-wholesale-assistant-
```

**Then run setup:**
```bash
# 1. Run setup script
./setup_macos.sh

# If you get permission error:
chmod +x setup_macos.sh
./setup_macos.sh
```

## Daily Development

### Start App on iPhone Simulator

```bash
# Option 1: Auto-open simulator and run
open -a Simulator && flutter run

# Option 2: Specify device
flutter devices                    # List available simulators
flutter run -d "iPhone 15 Pro"     # Run on specific simulator
```

### Hot Reload (While App is Running)

- **`r`** - Hot reload (saves state, updates UI instantly)
- **`R`** - Hot restart (resets state, fresh start)
- **`q`** - Quit app

### Common Commands

```bash
# Install/update dependencies
flutter pub get

# Check setup health
flutter doctor -v

# Clean build cache
flutter clean

# Run in release mode (better performance)
flutter run --release

# Open Xcode project
open ios/Runner.xcworkspace
```

## Troubleshooting

### "No devices found"
```bash
# Make sure simulator is running
open -a Simulator
# Wait 30 seconds, then:
flutter run
```

### "CocoaPods not installed"
```bash
sudo gem install cocoapods
cd ios && pod install && cd ..
```

### "Build failed"
```bash
flutter clean
flutter pub get
cd ios && pod install && cd ..
flutter run
```

### Simulator is slow
```bash
# Use release mode for better performance
flutter run --release

# Or test on physical device
flutter run -d <your-iphone-name>
```

## Build for App Store

```bash
# Open in Xcode
open ios/Runner.xcworkspace

# In Xcode:
# 1. Product > Archive
# 2. Distribute App
# 3. Upload to App Store Connect
```

## Resources

- [Full Setup Guide](MACOS_SETUP.md)
- [Flutter Docs](https://docs.flutter.dev/)
- [Xcode Help](https://developer.apple.com/xcode/)
