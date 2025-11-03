## Copilot / AI agent instructions for this repo

**Product:** "Sourcer" – AI-powered wholesale assistant for real-estate deal analysis and offer generation.

### Core business logic (implement exactly as specified)

**MAO Formula (Maximum Allowable Offer)**
```
MAO = (ARV × Factor) − Repairs − Assignment Fee
```
- Default Factor: `0.65`, user-adjustable range `0.55–0.75`
- ARV (After Repair Value): derived from comps with adjustments
- Repairs: AI-estimated line-item budget using ZIP-based standard rates (labor/material by trade)
- Assignment Fee: user-configurable per deal

**Offer Range Output**
- Aggressive: Factor `0.75`, lower repair buffer
- Target: Factor `0.65` (default), mid-range repairs
- Safe: Factor `0.55`, higher repair buffer

**Repair Estimation Logic**
- Pull ZIP-based standard pricing tables (labor/material rates by trade: electrical, plumbing, HVAC, flooring, etc.)
- AI generates line-item budget based on property condition signals (DOM, listing description, comps)
- Return itemized repair cost breakdown with trade, labor, material, total per line

**Comp Analysis**
- Fetch comparable sales (recent sold properties within radius/ZIP)
- Apply adjustments for: sqft, bed/bath count, condition, location, DOM (Days on Market)
- Show comp set with adjustment rationale in UI

### Architecture & components

**Cross-platform targets:** iOS, Android, Web (responsive)
- Consider React Native + Expo for mobile, Next.js for web, or unified framework
- Share business logic (MAO, repair estimation, comp scoring) across platforms

**Service boundaries**
- **Frontend:** Input (URL/address/ZIP), sliders (Factor, fee, risk), deal pipeline UI, PDF/text export
- **Backend/API:** Listing data ingestion, comps API integration, repair pricing lookup, MAO calculation, AI repair estimation, negotiation script generation
- **Data layer:** Deal pipeline storage, ZIP pricing tables, comp cache, user settings

**Key UI components to implement**
1. Address/URL input + ZIP search
2. Offer Range display (Aggressive/Target/Safe cards)
3. Comp set table with adjustments
4. Repair budget line-item table (trade, labor, material, total)
5. Negotiation scripts panel
6. One-tap PDF/textable offer generator
7. Deal pipeline (save/export CSV)
8. Sliders: risk tolerance, Factor (0.55–0.75), assignment fee

### Integration points & external dependencies

**Required integrations**
- Real-estate listing APIs (Zillow, Realtor.com, MLS feeds) – handle rate limits, caching
- Public property data (county records, tax assessor) – fallback if listing unavailable
- ZIP code pricing database (labor/material rates by trade) – maintain lookup tables or API
- AI service (OpenAI, Claude, or local LLM) for repair estimation and script generation
- PDF generation library (for offer sheets)
- SMS/webhook API (Twilio or similar) for textable offers
- CRM sync webhooks (Zapier, REsimpli, Podio)

**Data sources & citations**
- Always cite data sources in UI (e.g., "Comps from Zillow API", "Repair rates: RSMeans 2025 ZIP avg")
- Include disclaimers: "Estimates only, not financial/legal advice. Verify all data."

### Developer workflows

**Stack detection (check in order)**
1. Look for `package.json` (Node/React/Next.js) → `npm install && npm run dev`
2. Look for `pyproject.toml`/`requirements.txt` (Python/FastAPI/Django) → `python -m venv .venv && pip install -r requirements.txt && pytest`
3. Look for `Dockerfile` + `docker-compose.yml` → `docker-compose up`
4. If none exist, scaffold based on product requirements (recommend: Next.js frontend + Python FastAPI backend + Postgres)

**Testing priorities**
- Unit tests for MAO calculation (edge cases: negative repairs, Factor out of range)
- Integration tests for API data fetching (mock responses)
- E2E tests for critical path: input address → fetch comps → calculate MAO → generate PDF

### Project-specific conventions

**Code organization**
- `/frontend` or `/app`: UI components, screens, navigation
- `/backend` or `/api`: MAO logic, comp fetching, repair estimation, data models
- `/shared` or `/lib`: Cross-platform business logic (MAO formula, pricing tables)
- `/data`: ZIP pricing tables, sample comps for testing, mock listings

**Naming conventions**
- Use domain terms: `ARV`, `MAO`, `comp`, `repair_budget`, `assignment_fee`, `DOM`
- API endpoints: `/api/comps`, `/api/mao`, `/api/repairs`, `/api/offers`, `/api/deals`

**Configuration management**
- Store API keys in `.env` (never commit)
- Expose Factor range, default fee, ZIP pricing source as config
- Allow override of AI model endpoint (for local vs. cloud)

### When adding new features

**Before implementing:**
1. Verify the feature aligns with the 5 core outputs: Offer Range, Comp Set, Repair Budget, Negotiation Scripts, PDF/Text Export
2. Check if it requires new external API integrations → add to integration docs
3. Ensure cross-platform compatibility (iOS/Android/Web)
4. Add appropriate disclaimers if displaying financial estimates

**Examples of good PRs**
- "Implement MAO calculation with Factor slider (0.55–0.75) and unit tests"
- "Add ZIP pricing table lookup for electrical/plumbing trades with RSMeans 2025 data"
- "Integrate Zillow API for comp fetching with rate limit handling and cache layer"

If you need clarification on MAO logic, repair estimation AI prompts, or specific API integrations, ask before implementing.
