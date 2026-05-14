PROJECT DOOMSDAY — Complete Context Document
For Future Conversation Continuity
1. WHAT IS THIS PROJECT
Project Doomsday is a personal project by the user (Moosa) — an institutional-grade financial intelligence engine built as a Streamlit web application. It stress-tests company valuations against global "Black Swan" events using multi-agent AI.

Core concept: User enters a stock ticker → system pulls live financial data → AI agents identify risks across 5 domains → adversarial debate validates risks → geographic mapping plots vulnerabilities → distressed valuation shows potential downside.

Built for: Milan AI Week Hackathon (but is a personal ongoing project)

2. TECH STACK
Component	Technology
Frontend	Streamlit (Python)
Visualization	Plotly (maps, waterfall charts, radar)
Financial Data	Yahoo Finance (yfinance)
News/Search	Tavily API
Primary AI	Google Gemini 2.0 Flash
Fallback AI 1	NVIDIA Llama 3.1 Nemotron 70B
Fallback AI 2	Fireworks AI (Llama models)
Styling	Custom CSS (dark military "monitor" aesthetic)
Maps	Plotly Scattermapbox with carto-darkmatter tiles
Folder Structure:

C:\Users\Moosa\Downloads\Project_Doomsday\
├── app.py                    # Main application (THE file we've been working on)
├── valuation_engine.py       # Separate valuation module (exists but app.py is now self-contained)
├── filing_intelligence.py    # SEC/SEBI filing extraction (exists but app.py works without it)
├── .env                      # API keys
├── requirements.txt          # Dependencies
3. CURRENT STATE (as of last working session)
What's Working:
UI/Theme: Dark military aesthetic with JetBrains Mono font, red accent colors, pulsing threat badges — USER LOVES THIS, DO NOT CHANGE
Map: Carto-darkmatter style with curved orange/red lines converging from risk nodes to company HQ — USER LOVES THIS
Waterfall Chart: Shows value destruction from base fair value down to distressed value — USER LOVES HOW THIS LOOKS
Risk Cards: WorldMonitor-style feed showing validated risks with severity badges
Adversarial Debate: Bear/Bull/Judge tribunal with expandable transcripts
Progressive Terminal Feed: Shows real-time swarm execution log during analysis
Chaos Slider: 0-1 slider that adjusts stress intensity in real-time without re-running AI
HQ Database: Known coordinates for US + Indian + Global company headquarters
What Was Broken and Fixed During Our Conversation:
Issue	Root Cause	Status
"Failed to fetch" Streamlit errors	Emojis/Unicode in code	FIXED - ASCII-clean
App stuck loading indefinitely	find_best_model() hanging on rate-limited APIs	FIXED - added run_with_timeout()
API keys not loading	.env not in correct directory / keys revoked	FIXED - added path resolution + manual parse fallback
Waterfall chart crashing	titlefont deprecated in newer Plotly	FIXED - replaced with title=dict(text=..., font=dict(...))
Map showing world 4 times	No bounds constraint	FIXED - added bounds=dict(west=-180, east=180, south=-70, north=80)
Fair value 2.5x market price (TSM $979 vs $391)	DCF model not anchored to market reality	FIXED - capped FV at 1.2x market for large caps
Downside showing +99% (upside)	distressed > current_price	FIXED - forced downside always negative for stress tool
Only 1 risk found	Tavily timeout + weak fallback	FIXED - added generate_fallback_risks() with sector-specific intelligent defaults
What User Explicitly Said They Like (DO NOT CHANGE):
The font (JetBrains Mono throughout)
The dark military aesthetic
The map with curved convergence lines
The waterfall chart visual style
The NVDA demo results (layout, data quality)
The risk card feed design
The adversarial debate format (Bear/Bull/Judge)
The metrics row at the top (Market Price, Base FV, Distressed, Downside%, Threat Level, Active Risks)
The progressive loading terminal
4. VALUATION METHODOLOGY (Critical — User Cares About This)
The system uses Context-Aware Routing — different formulas for different company types:

Company Type	Detection Logic	Method	Why Not DCF
Banks/Insurance	Sector contains "financial/bank/insurance"	P/BV + Excess Return	Debt is their product, not liability
High-Growth Tech	Revenue growth >25% AND low/no profit	EV/Revenue + Rule of 40	FCF is negative, terminal value >80%
Cyclical (Energy/Mining)	Sector contains "energy/mining/materials"	Normalized Mid-Cycle EBITDA	Current earnings misleading at peaks/troughs
Mature Profitable	Has positive EBITDA + net income, not above categories	5-Year FCF-DCF + Gordon Growth	Only valid DCF candidate
Loss-Making/Other	Everything else	EV/Revenue (discounted)	No earnings to discount
KEY RULE: Base Fair Value is CAPPED relative to market price:

Large cap (>$100B): max 1.2x current price
Mid cap ($10-100B): max 1.35x
Small cap (<$10B): max 1.5x
Rationale: This is a STRESS TEST tool, not a stock picker. We assume markets are roughly efficient. Our job is to model downside, not find undervalued stocks.

Stress Application:

Revenue haircut: chaos * 15 + (risk_severity/10) * 12
WACC premium: chaos * 4.5 + (risk_severity/10) * 3
Margin compression: chaos * 250 + risk_severity * 50 (in bps)
Multiple compression: 1 - (chaos * 0.18 + (risk_severity/10) * 0.12)
Downside is ALWAYS negative — if math produces positive, force minimum downside of -(chaos * 40 + risk_severity * 3)%

5. THE AGENTIC SWARM (Architecture)
User Input (Ticker + Chaos Level)
        │
        ▼
┌─────────────────────────┐
│ Step 1: AI Initialization│ ← DoomsdayAI class with failover chain
│ (Gemini → NVIDIA → FW)  │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Step 2: World State      │ ← yfinance (VIX, DXY, Oil, Gold, 10Y)
│ (Market Fear Assessment) │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Step 3: Company Profile  │ ← yfinance with currency conversion to USD
│ (Smart Ticker Resolution)│ ← Auto-resolves Indian tickers (.NS)
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Step 4: Intelligence Scan│ ← 6 Tavily queries across domains
│ (Multi-domain search)    │ ← LLM synthesis into 6 risks
│                          │ ← Fallback: sector-specific defaults
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Step 5: Adversarial      │ ← For each risk:
│ Debate (per risk)        │   Bear Advocate → Bull Advocate → Judge
│                          │   Judge assigns final severity + probability
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Step 6: Geographic Map   │ ← Coordinate database lookup
│ (Fracture Nodes)         │ ← Plots nodes + curved lines to HQ
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Step 7: Valuation        │ ← Method routing based on company type
│ (Stress Calculation)     │ ← Waterfall data generation
└───────────┬─────────────┘
            ▼
        RENDER RESULTS
6. INDIAN TICKER HANDLING
Auto-resolution: If user types "RELIANCE", system tries with .NS suffix automatically
Known Indian tickers list: ~55 major NSE tickers hardcoded for instant resolution
Currency: ALL data converted to USD using live FX rates from yfinance (USDINR=X)
Fallback FX rates: If live FX fails, uses hardcoded approximations (INR=83.5, etc.)
Display: Everything shown in USD and billions regardless of origin market
HQ Database: Indian companies mapped to correct cities (Mumbai, Bangalore, Delhi, etc.)
7. KEY TECHNICAL DECISIONS
run_with_timeout() — Every external call (API, yfinance, Tavily) wrapped with timeout (8-45 seconds depending on operation). Prevents infinite hangs.

parse_json_safe() — Strips markdown code blocks, finds JSON in text, handles partial responses. Critical because LLMs sometimes wrap JSON in ```json ```.

Session State — All analysis results stored in st.session_state. Chaos slider updates only re-run compute_valuation() (instant), NOT the full pipeline (which takes 30-60 seconds).

Fallback Risks — generate_fallback_risks() provides 5-6 intelligent sector-specific risks when AI/Tavily fails. Ensures the tool ALWAYS produces output.

ASCII-Clean — Zero emojis anywhere in the code. All indicators are text: [!], [CRITICAL], [HIGH], etc.

Self-Contained — app.py works WITHOUT valuation_engine.py or filing_intelligence.py. All critical logic is embedded.

8. SECURITY INCIDENT
During development, an AI coding assistant (in Windsurf/Cursor-type IDE) read the .env file and exposed API keys in a cloud-processed chat. User was advised to:

Revoke all exposed keys immediately
Generate new keys
Add .env to AI ignore files
Check IDE AI agent file access permissions
9. KNOWN REMAINING ISSUES / FUTURE WORK
Item	Status	Notes
SEC EDGAR deep parsing	Not implemented	User mentioned wanting 10-K Item 1A extraction
SEBI/BSE filing integration	Not implemented	For Indian companies
PDF Memo Export	Not implemented	McKinsey-style IC memo
Macro feedback loops	Not implemented	Chaos > 0.8 should auto-spike VIX/Oil in simulation
Search result caching	Not implemented	To prevent Tavily rate limits
"Lying Gap" detection	Not implemented	News contradicting filings = alpha signal
Map bounds issue	Fixed but may need tuning	Added bounds constraint
Valuation for specific edge cases	Ongoing	e.g. companies with negative book value, SPACs
10. HOW TO GIVE CONTEXT NEXT TIME
Paste this entire document as your first message, then add:

"This is the context from our previous session. The app.py is currently working with 
[describe current state — e.g., "working for NVDA and TSM but Indian tickers still 
have currency issues"]. I need help with [specific problem]."
Important reminders for future AI assistant:

DO NOT change fonts, colors, or visual aesthetic
DO NOT change how the map looks (curved lines, dark theme)
DO NOT change the waterfall chart style
DO NOT add emojis anywhere
The user runs this on Windows at C:\Users\Moosa\Downloads\Project_Doomsday\
The user's primary AI provider is Gemini (Google)
The user also has NVIDIA API access
All values must be in USD regardless of company origin
Valuation must always show DOWNSIDE (negative %) not upside
11. REQUIREMENTS.TXT
streamlit>=1.28.0
plotly>=5.18.0
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.31
python-dotenv>=1.0.0
google-genai>=0.3.0
openai>=1.12.0
tavily-python>=0.3.0
12. .ENV STRUCTURE
GOOGLE_API_KEY=AIzaSy...
TAVILY_API_KEY=tvly-...
NVIDIA_API_KEY=nvapi-...  (optional)
FIREWORKS_API_KEY=fw_...  (optional)
End of context document. Last updated: Current session.