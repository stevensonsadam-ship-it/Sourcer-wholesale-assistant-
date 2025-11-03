#!/bin/bash
# Quick deploy script for Sourcer web app

set -e

echo "🚀 Sourcer - Quick Web Deploy"
echo "================================"
echo ""

cd "$(dirname "$0")"

echo "📦 Building web app..."
npm run build:web

echo ""
echo "✅ Build complete! (316KB)"
echo ""
echo "🌐 Choose deployment method:"
echo ""
echo "1. Vercel (recommended - fastest)"
echo "   → vercel --prod"
echo ""
echo "2. Netlify"
echo "   → netlify deploy --prod --dir=dist"
echo ""
echo "3. Manual (upload dist/ folder to any host)"
echo ""
echo "Ready to deploy with Vercel? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Deploying to Vercel..."
    vercel --prod
else
    echo ""
    echo "📁 Build output is in: dist/"
    echo "You can deploy manually or use: vercel --prod"
fi
