# Sourcer Backend API

Simple Express backend for fetching Zillow data and generating repair estimates.

## Setup

```bash
cd backend
npm install
npm start
```

Server runs on http://localhost:3000

## API Endpoints

### POST /api/estimateFromZillow

Scrapes Zillow listing URL and returns repair estimates.

**Request:**
```json
{
  "url": "https://www.zillow.com/homedetails/123-Main-St...",
  "zipcode": "77033",
  "sqft": 1500,
  "dealId": "unique-id"
}
```

**Response:**
```json
{
  "items": [
    {
      "key": "paint",
      "label": "Interior paint",
      "amount": 3750,
      "confidence": 0.85
    },
    ...
  ],
  "arv": 250000,
  "source": "zillow",
  "timestamp": "2025-11-03T08:30:00.000Z"
}
```

## Next Steps

1. Add real Zillow scraping with `axios` + `cheerio`
2. Integrate AI (OpenAI/Claude) for condition assessment
3. Add ZIP-based pricing multipliers
4. Store estimates in database
5. Add authentication
