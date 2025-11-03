// Simple Express backend for Sourcer - Zillow data scraping
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const cheerio = require('cheerio');
const puppeteer = require('puppeteer');
const app = express();

// Use Puppeteer for real Zillow scraping
const USE_PUPPETEER = process.env.USE_PUPPETEER === 'true' || false;

app.use(cors());
app.use(express.json());

// GET / - API status page
app.get('/', (req, res) => {
  res.json({
    name: 'Sourcer Backend API',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      estimate: 'POST /api/estimateFromZillow'
    },
    timestamp: new Date().toISOString()
  });
});

// POST /api/estimateFromZillow
// Scrapes Zillow listing and returns repair estimates
app.post('/api/estimateFromZillow', async (req, res) => {
  const { url, zipcode, sqft, bedrooms, bathrooms, yearBuilt } = req.body;
  
  console.log('🔍 Scraping Zillow:', url);
  console.log('📋 Manual inputs:', { sqft, bedrooms, bathrooms, yearBuilt });
  
  try {
    // Use manual inputs if provided, otherwise scrape
    let zillowData;
    
    if (sqft && bedrooms && bathrooms) {
      // Use manual inputs
      console.log('✅ Using manual inputs (no scraping needed)');
      zillowData = {
        success: true,
        price: 0,
        address: 'Manual Entry',
        sqft: parseInt(sqft),
        bedrooms: parseInt(bedrooms),
        bathrooms: parseFloat(bathrooms),
        yearBuilt: parseInt(yearBuilt) || 1980,
        source: 'manual'
      };
    } else {
      // Scrape Zillow listing
      zillowData = USE_PUPPETEER 
        ? await scrapeZillowWithPuppeteer(url)
        : await scrapeZillow(url);
    }
    
    if (!zillowData.success) {
      console.log('⚠️  Scraping failed, using fallback estimates');
      return res.json(generateFallbackEstimate(sqft || 1500, zipcode));
    }
    
    console.log('✅ Scraped data:', zillowData);
    
    // Generate repair estimates based on scraped data
    const propertySquareFeet = zillowData.sqft || sqft || 1500;
    const bedrooms = zillowData.bedrooms || 3;
    const bathrooms = zillowData.bathrooms || 2;
    const yearBuilt = zillowData.yearBuilt || 1980;
    const price = zillowData.price || 0;
    
    // Calculate repair estimates based on property condition
    const age = new Date().getFullYear() - yearBuilt;
    const conditionMultiplier = age > 50 ? 1.4 : age > 30 ? 1.2 : age > 15 ? 1.0 : 0.8;
    
    const repairItems = [
      { 
        key: 'paint', 
        label: 'Interior paint', 
        amount: Math.round(propertySquareFeet * 2.2 * conditionMultiplier), 
        confidence: 0.85 
      },
      { 
        key: 'flooring', 
        label: 'Flooring (LVP/carpet)', 
        amount: Math.round(propertySquareFeet * 3.5 * conditionMultiplier), 
        confidence: 0.80 
      },
      { 
        key: 'kitchen', 
        label: 'Kitchen refresh', 
        amount: Math.round((6000 + bedrooms * 1000) * conditionMultiplier), 
        confidence: 0.70 
      },
      { 
        key: 'bathrooms', 
        label: `Bathroom updates (${bathrooms} bath)`, 
        amount: Math.round(bathrooms * 2800 * conditionMultiplier), 
        confidence: 0.75 
      },
      { 
        key: 'roof', 
        label: 'Roof repair/allowance', 
        amount: age > 20 ? Math.round(3500 * conditionMultiplier) : 1500, 
        confidence: age > 20 ? 0.80 : 0.50 
      },
      { 
        key: 'hvac', 
        label: 'HVAC service/replace', 
        amount: age > 15 ? Math.round(1200 * conditionMultiplier) : 600, 
        confidence: 0.85 
      },
      { 
        key: 'electrical', 
        label: 'Electrical/Plumbing', 
        amount: Math.round((1500 + propertySquareFeet * 0.5) * conditionMultiplier), 
        confidence: 0.70 
      },
      { 
        key: 'windows', 
        label: 'Windows/doors', 
        amount: age > 30 ? Math.round(2500 * conditionMultiplier) : 800, 
        confidence: age > 30 ? 0.75 : 0.50 
      },
      { 
        key: 'cleanup', 
        label: 'Cleanup/landscaping', 
        amount: Math.round(1200 + propertySquareFeet * 0.2), 
        confidence: 0.90 
      },
    ];
    
    // Calculate total and add contingency
    const totalRepairs = repairItems.reduce((sum, item) => sum + item.amount, 0);
    repairItems.push({
      key: 'contingency',
      label: 'Contingency (10%)',
      amount: Math.round(totalRepairs * 0.1),
      confidence: 1.0
    });
    
    // Estimate ARV (After Repair Value) - typically 85-90% of list price for distressed properties
    const estimatedARV = price > 0 ? Math.round(price * 1.15) : Math.round(propertySquareFeet * 180);
    
    res.json({
      items: repairItems,
      arv: estimatedARV,
      source: 'zillow',
      propertyData: {
        address: zillowData.address,
        sqft: propertySquareFeet,
        bedrooms,
        bathrooms,
        yearBuilt,
        price,
        age,
        conditionMultiplier
      },
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    // Fallback to estimates based on sqft
    res.json(generateFallbackEstimate(sqft || 1500, zipcode));
  }
});

// Scrape Zillow listing page
async function scrapeZillow(url) {
  try {
    // Add user agent to avoid being blocked
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
      },
      timeout: 10000
    });
    
    const $ = cheerio.load(response.data);
    
    // Extract property details from Zillow HTML
    // Note: Zillow structure changes frequently, these selectors may need updates
    
    // Try to find price
    let price = 0;
    const priceText = $('span[data-testid="price"]').text() || 
                     $('h3.ds-price').text() ||
                     $('span.ds-value').first().text();
    price = parseInt(priceText.replace(/[^0-9]/g, '')) || 0;
    
    // Try to find address
    const address = $('h1[class*="address"]').text().trim() || 
                   $('h1.ds-address-container').text().trim() ||
                   'Address not found';
    
    // Try to find square footage
    let sqft = 0;
    $('span').each((i, elem) => {
      const text = $(elem).text();
      if (text.includes('sqft') && !sqft) {
        sqft = parseInt(text.replace(/[^0-9]/g, '')) || 0;
      }
    });
    
    // Try to find bedrooms
    let bedrooms = 3;
    $('span').each((i, elem) => {
      const text = $(elem).text();
      if ((text.includes('bd') || text.includes('Bed')) && !isNaN(parseInt(text))) {
        bedrooms = parseInt(text.replace(/[^0-9]/g, '')) || 3;
      }
    });
    
    // Try to find bathrooms
    let bathrooms = 2;
    $('span').each((i, elem) => {
      const text = $(elem).text();
      if ((text.includes('ba') || text.includes('Bath')) && !isNaN(parseFloat(text))) {
        bathrooms = parseFloat(text.replace(/[^0-9.]/g, '')) || 2;
      }
    });
    
    // Try to find year built
    let yearBuilt = 1980;
    $('span').each((i, elem) => {
      const text = $(elem).text();
      if (text.includes('Built in') || text.includes('Year built')) {
        const match = text.match(/\d{4}/);
        if (match) yearBuilt = parseInt(match[0]);
      }
    });
    
    console.log('📊 Extracted:', { price, address, sqft, bedrooms, bathrooms, yearBuilt });
    
    return {
      success: !!(price || sqft), // Consider successful if we got price or sqft
      price,
      address,
      sqft,
      bedrooms,
      bathrooms,
      yearBuilt
    };
    
  } catch (error) {
    console.error('Scraping error:', error.message);
    return { success: false };
  }
}

// Scrape Zillow with Puppeteer (browser automation - bypasses 403)
async function scrapeZillowWithPuppeteer(url) {
  let browser;
  try {
    console.log('🚀 Launching Puppeteer browser...');
    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--single-process',
        '--disable-gpu'
      ]
    });
    
    const page = await browser.newPage();
    
    // Set realistic viewport and user agent
    await page.setViewport({ width: 1920, height: 1080 });
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    
    console.log('🌐 Loading page:', url);
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
    
    // Wait for content to load
    await page.waitForTimeout(2000);
    
    // Extract data from the page
    const data = await page.evaluate(() => {
      // Try multiple selectors for each field
      const getText = (selectors) => {
        for (const selector of selectors) {
          const el = document.querySelector(selector);
          if (el) return el.textContent.trim();
        }
        return null;
      };
      
      const priceText = getText([
        'span[data-testid="price"]',
        'h3.ds-price',
        'span.ds-value',
        '[class*="price"]'
      ]);
      
      const addressText = getText([
        'h1[data-testid="address"]',
        'h1.ds-address-container',
        'h1[class*="address"]'
      ]);
      
      const bedsText = getText([
        'span[data-testid="bed-bath-item"]:first-child',
        'span.ds-bed-bath-living-area-container span:first-child'
      ]);
      
      const bathsText = getText([
        'span[data-testid="bed-bath-item"]:nth-child(2)',
        'span.ds-bed-bath-living-area-container span:nth-child(2)'
      ]);
      
      const sqftText = getText([
        'span[data-testid="bed-bath-beyond"]',
        'span[data-testid="bed-bath-item"]:last-child',
        'span.ds-bed-bath-living-area-container span:last-child'
      ]);
      
      // Look for year built in facts section
      let yearBuilt = null;
      const factElements = document.querySelectorAll('span, div, li');
      factElements.forEach(el => {
        const text = el.textContent;
        if (text.includes('Built in') || text.includes('Year built')) {
          const match = text.match(/\d{4}/);
          if (match) yearBuilt = match[0];
        }
      });
      
      return {
        priceText,
        addressText,
        bedsText,
        bathsText,
        sqftText,
        yearBuilt
      };
    });
    
    console.log('📊 Raw scraped data:', data);
    
    // Parse the extracted data
    const price = data.priceText ? parseInt(data.priceText.replace(/[^0-9]/g, '')) : 0;
    const address = data.addressText || 'Address not found';
    const bedrooms = data.bedsText ? parseInt(data.bedsText.replace(/[^0-9]/g, '')) : 3;
    const bathrooms = data.bathsText ? parseFloat(data.bathsText.replace(/[^0-9.]/g, '')) : 2;
    const sqft = data.sqftText ? parseInt(data.sqftText.replace(/[^0-9]/g, '')) : 0;
    const yearBuilt = data.yearBuilt ? parseInt(data.yearBuilt) : 1980;
    
    await browser.close();
    
    console.log('✅ Puppeteer scraped:', { price, address, sqft, bedrooms, bathrooms, yearBuilt });
    
    return {
      success: !!(price || sqft),
      price,
      address,
      sqft,
      bedrooms,
      bathrooms,
      yearBuilt,
      source: 'puppeteer'
    };
    
  } catch (error) {
    console.error('❌ Puppeteer error:', error.message);
    if (browser) await browser.close();
    return { success: false };
  }
}

// Generate fallback estimates when scraping fails
function generateFallbackEstimate(sqft, zipcode) {
  const conditionMultiplier = 1.0;
  
  const items = [
    { key: 'paint', label: 'Interior paint (estimated)', amount: Math.round(sqft * 2.5), confidence: 0.60 },
    { key: 'flooring', label: 'Flooring (estimated)', amount: Math.round(sqft * 3.8), confidence: 0.60 },
    { key: 'kitchen', label: 'Kitchen refresh (estimated)', amount: 7500, confidence: 0.50 },
    { key: 'bathrooms', label: 'Bathroom updates (estimated)', amount: 5200, confidence: 0.50 },
    { key: 'roof', label: 'Roof repair (estimated)', amount: 3000, confidence: 0.40 },
    { key: 'hvac', label: 'HVAC service (estimated)', amount: 800, confidence: 0.60 },
    { key: 'electrical', label: 'Electrical/Plumbing (estimated)', amount: 1800, confidence: 0.50 },
    { key: 'cleanup', label: 'Cleanup (estimated)', amount: 1200, confidence: 0.70 },
  ];
  
  const total = items.reduce((sum, item) => sum + item.amount, 0);
  items.push({ key: 'contingency', label: 'Contingency (10%)', amount: Math.round(total * 0.1), confidence: 1.0 });
  
  return {
    items,
    arv: Math.round(sqft * 180),
    source: 'fallback',
    message: 'Could not scrape Zillow. Using generic estimates based on square footage.',
    timestamp: new Date().toISOString()
  };
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 Sourcer backend running on http://localhost:${PORT}`);
  console.log(`📊 API endpoint: http://localhost:${PORT}/api/estimateFromZillow`);
});
