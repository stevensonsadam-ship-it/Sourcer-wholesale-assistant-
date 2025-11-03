#!/bin/bash
# Quick setup script for macOS
# Run this on your local macOS machine

echo "🍎 Sourcer - macOS Setup Script"
echo "================================"

# Check Flutter installation
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter not found. Please install Flutter first:"
    echo "   https://docs.flutter.dev/get-started/install/macos"
    exit 1
fi

echo "✅ Flutter found: $(flutter --version | head -1)"

# Check Xcode
if ! command -v xcrun &> /dev/null; then
    echo "❌ Xcode not found. Please install from App Store"
    exit 1
fi

echo "✅ Xcode found"

# Install dependencies
echo ""
echo "📦 Installing Flutter dependencies..."
flutter pub get

# Check CocoaPods
if ! command -v pod &> /dev/null; then
    echo "⚠️  CocoaPods not found. Installing..."
    sudo gem install cocoapods
fi

# Setup iOS dependencies
echo ""
echo "📱 Setting up iOS dependencies..."
cd ios
pod install || pod repo update && pod install
cd ..

# Run Flutter doctor
echo ""
echo "🔍 Running Flutter doctor..."
flutter doctor

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the app:"
echo "   1. Open Simulator: open -a Simulator"
echo "   2. Run app: flutter run"
echo ""
echo "   OR open in Xcode: open ios/Runner.xcworkspace"
