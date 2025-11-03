# Zillow Web Scraping Guide

## Current Status

✅ **Web scraping implemented** with graceful fallback
⚠️  **Zillow blocks requests** with 403 (anti-bot protection)
✅ **Fallback estimates work** based on square footage

## How It Works

1. **Primary Method**: Try to scrape Zillow HTML for:
   - Price
   - Address
   - Square footage
   - Bedrooms/bathrooms
   - Year built

2. **Fallback Method**: If scraping fails (403/timeout), use generic estimates based on:
   - Square footage (from user input)
   - ZIP code multipliers
   - Industry-standard repair costs

## Zillow Anti-Bot Protection

Zillow uses multiple protection layers:
- IP rate limiting
- User-agent detection
- JavaScript rendering (dynamic content)
- Captcha challenges
- TLS fingerprinting

## Solutions to Get Real Data

### Option 1: Use Zillow's Official API (RECOMMENDED)
```bash
# Sign up at: https://www.zillow.com/howto/api/APIOverview.htm
# Note: Zillow deprecated public API in 2021
# Alternative: Use Bridge Interactive or other MLS data providers
```

### Option 2: Use a Proxy Service
```javascript
// Add to backend/server.js
const ScraperAPI = require('scraperapi-sdk')('YOUR_API_KEY');

async function scrapeZillow(url) {
  const response = await ScraperAPI.get(url);
  // Parse response.text with Cheerio
}
```

**Proxy Services:**
- ScraperAPI: https://www.scraperapi.com/ ($49/mo for 100k requests)
- Bright Data: https://brightdata.com/
- Oxylabs: https://oxylabs.io/

### Option 3: Use RapidAPI Real Estate APIs
```javascript
// RapidAPI has multiple real estate data APIs
const response = await axios.get('https://zillow56.p.rapidapi.com/search', {
  params: { location: '77033' },
  headers: {
    'X-RapidAPI-Key': 'YOUR_KEY',
    'X-RapidAPI-Host': 'zillow56.p.rapidapi.com'
  }
});
```

**RapidAPI Options:**
- Zillow API: https://rapidapi.com/apimaker/api/zillow-com1
- Realty in US: https://rapidapi.com/apidojo/api/realty-in-us
- Cost: $0-$50/mo depending on usage

### Option 4: Use Puppeteer (Browser Automation)
```javascript
const puppeteer = require('puppeteer');

async function scrapeZillow(url) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  // Set realistic viewport and user agent
  await page.setUserAgent('Mozilla/5.0...');
  await page.goto(url, { waitUntil: 'networkidle2' });
  
  const data = await page.evaluate(() => {
    return {
      price: document.querySelector('[data-testid="price"]')?.textContent,
      sqft: document.querySelector('[data-testid="bed-bath-sqft"]')?.textContent
    };
  });
  
  await browser.close();
  return data;
}
```

**Installation:**
```bash
npm install puppeteer
```

### Option 5: Manual Data Entry (Current Workaround)
Users can manually enter:
- Square footage in the UI
- Bedrooms/bathrooms (add fields)
- Year built (add field)

The system will generate accurate estimates based on these inputs.

## Testing the Current System

### Test with Fallback Estimates (Works Now)
```bash
curl -X POST http://localhost:3000/api/estimateFromZillow \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.zillow.com/homedetails/123-Main-St",
    "zipcode": "77033",
    "sqft": 1800
  }'
```

### Expected Response
```json
{
  "items": [
    {"key": "paint", "label": "Interior paint (estimated)", "amount": 4500},
    {"key": "flooring", "label": "Flooring (estimated)", "amount": 6840},
    ...
  ],
  "arv": 324000,
  "source": "fallback",
  "message": "Could not scrape Zillow. Using generic estimates...",
  "timestamp": "2025-11-03T08:30:00.000Z"
}
```

## Recommendations

1. **Short-term**: Use current fallback system + manual entry
2. **Medium-term**: Add RapidAPI integration ($20/mo budget)
3. **Long-term**: Subscribe to MLS data feed or Bridge Interactive

## Add Manual Input Fields to Flutter App

To improve accuracy without scraping, add these fields to `lib/main.dart`:

```dart
final sqftCtrl = TextEditingController(text: '1500');
final bedsCtrl = TextEditingController(text: '3');
final bathsCtrl = TextEditingController(text: '2');
final yearCtrl = TextEditingController(text: '1980');
```

Then pass to API:
```dart
body: jsonEncode({
  'url': urlCtrl.text,
  'zipcode': zipCtrl.text,
  'sqft': int.tryParse(sqftCtrl.text),
  'bedrooms': int.tryParse(bedsCtrl.text),
  'bathrooms': double.tryParse(bathsCtrl.text),
  'yearBuilt': int.tryParse(yearCtrl.text),
}),
```

## Next Steps

1. ✅ Web scraping implemented (with fallback)
2. ⏳ Choose data provider (RapidAPI recommended)
3. ⏳ Add manual input fields for property details
4. ⏳ Integrate MLS data feed (for production)
