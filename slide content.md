Project Doomsday — Slide Deck Content (7 Slides)
SLIDE 1: Title + Hook
Title: PROJECT DOOMSDAY

Subtitle: Multi-Agent Black Swan Stress-Testing Engine

Tagline: "Every portfolio has a breaking point. We find it in 60 seconds."

Visual suggestion: Dark background, the fracture map screenshot with curved orange lines converging on a company HQ

Bottom bar:

Milan AI Week Hackathon 2025
Built with: Google Gemini 2.0 Flash | Tavily | Streamlit
Creator: Moosa | IIM [your campus]
SLIDE 2: The Problem
Header: The Problem: Blind Spots Kill Portfolios

Content:

Traditional financial models assume normal distributions — they break precisely when you need them most (2008, COVID, SVB collapse)

Analysts identify risks in isolation — they miss second-order cascades and geographic convergence

Existing stress-test tools are either:

Too simplistic (flat % haircuts with no intelligence behind them)
Too slow (weeks of manual scenario analysis by research teams)
Black boxes (no transparency into assumptions or methodology)
The gap: There is no tool that identifies specific, current Black Swan risks for a given company, validates them adversarially, maps their geographic propagation, models contagion cascades, and computes distressed valuations — transparently, in under 60 seconds.

Stat to include: "93% of institutional investors say tail risk is their #1 concern, yet only 12% have systematic tools to model it." — CFA Institute 2024 Survey

SLIDE 3: The Solution — Architecture
Header: Project Doomsday: How It Works

Visual: Flow diagram (simplified version of the 7-step pipeline)

USER INPUT (Ticker + Chaos Level)
        |
        v
[1] AI INITIALIZATION -----> Google Gemini 2.0 Flash (via Google AI Studio)
        |                     Failover: NVIDIA NIM / Fireworks AI
        v
[2] WORLD STATE -----------> Live VIX, Oil, Gold, Yields (yfinance)
        |                     Global Fear Classification
        v
[3] COMPANY PROFILE -------> Smart ticker resolution (US/India/Global)
        |                     Auto currency normalization to USD
        v
[4] INTELLIGENCE SCAN -----> 6 parallel Tavily search vectors
        |                     Gemini synthesizes into 6 material risks
        v
[5] ADVERSARIAL TRIBUNAL --> Bear Agent | Bull Agent | Judge Agent
        |                     3-agent debate per risk (Gemini-powered)
        v
[6] GEOGRAPHIC MAPPING ----> Fracture nodes + curved convergence lines
        |                     Plotly dark-matter world map
        v
[7] VALUATION + CASCADE ---> 5-path methodology routing
                              Contagion propagation modeling
                              Transparent stress waterfall
Key callout box: "5 AI agents working in coordination — Intelligence Analyst, Bear Advocate, Bull Advocate, Fracture Judge, and Contagion Modeler — all powered by Gemini 2.0 Flash via Google AI Studio"

SLIDE 4: The AI Agents — Multi-Agent System
Header: Agentic AI: 5 Specialized Agents in Coordinated Swarm

Content (card layout, one per agent):

Agent	Role	Temperature	What It Does
Intelligence Analyst	Risk Discovery	0.5	Synthesizes 6 Tavily search vectors + company fundamentals into 6 specific, geolocated risk scenarios with severity, probability, and revenue-at-risk estimates
Bear Advocate	Prosecution	0.6	Argues worst-case with historical precedents, specific numbers, and catastrophic framing. Pushes severity UP.
Bull Advocate	Defense	0.6	Challenges evidence, presents mitigating factors, argues market has priced it in. Pushes severity DOWN.
Fracture Judge	Verdict	0.3	Low-temperature, high-conviction. Calibrated rubric: 8+ catastrophic, 6-7 material, <4 dismissed. Final authority on severity and probability.
Contagion Modeler	Cascade	0.5	Models 2nd/3rd/4th order propagation effects. Traces how a single shock cascades through P&L → credit → refinancing → capex over weeks-to-months.
Why multi-agent?

Single-agent systems are confirmation-biased — they find what they expect
Adversarial architecture forces steel-manning of both sides before judgment
Mimics real institutional process: Research Analyst → IC Debate → PM Decision
Judge at T=0.3 provides calibrated, low-variance final scores
Tech note: All agents use Google Gemini 2.0 Flash via Google AI Studio API. Structured JSON output mode ensures parseable responses. Automatic failover to NVIDIA NIM (Llama 3.3 70B) and Fireworks AI if primary model is rate-limited.

SLIDE 5: Key Differentiators + Demo Screenshots
Header: What Makes This Different

Left column — 4 differentiators:

1. Context-Aware Valuation (Not One-Size-Fits-All)

5 distinct methodologies routed by company type
Banks get P/BV (debt = product), cyclicals get normalized EBITDA (spot earnings mislead), high-growth gets EV/Revenue (negative FCF breaks DCF)
Market-anchored: assumes efficiency, stresses downward only
2. Geographic Intelligence (Not Just Numbers)

Every risk mapped to physical coordinates
Curved convergence lines show vulnerability concentration
Visual answer to: "Where on Earth is my portfolio exposed?"
3. Contagion Cascades (Not Isolated Risks)

Models how Risk A triggers Effect B triggers Effect C
Compound correlation (rho → 1) as chaos increases
Inspired by Kiyotaki-Moore credit cycles and Minsky Moments
4. Full Transparency (No Black Boxes)

Every formula shown with numbers plugged in
Every routing decision explained with True/False flags
Every agent's reasoning visible in expandable transcripts
Reproducible: same inputs → same methodology → same output
Right column: 2-3 screenshots — fracture map, waterfall chart, valuation transparency panel

SLIDE 6: Business Model + Monetization
Header: Go-To-Market: From Hackathon to Product

The Market:

Global risk analytics market: $65B by 2027 (Allied Market Research)
Bloomberg Terminal: $25,000/year per seat — no AI-native stress testing
Hedge funds spend $2-5M/year on bespoke scenario analysis
Monetization Paths:

Tier	Target	Pricing	Value Prop
Free / Freemium	Retail investors, students	$0 (3 analyses/day)	Lead generation, community building
Pro	Independent analysts, RIAs, small funds	$99-299/month	Unlimited analyses, PDF memo export, portfolio-level stress testing, API access
Institutional	Hedge funds, PE firms, family offices	$2,000-10,000/month	Custom risk domains, private data integration (10-K parsing, SEBI filings), white-label, multi-portfolio dashboards, Slack/Teams alerts
API-as-a-Service	Fintech platforms, robo-advisors, brokerages	Per-call pricing	Embed stress-test capability into existing products
Competitive Moat:

Multi-agent adversarial validation (not single-prompt risk lists)
Real-time intelligence (Tavily) + structured reasoning (Gemini) = freshness + depth
Methodology transparency builds trust with compliance teams
Indian market support (NSE/BSE) — massively underserved by Western tools
Unit Economics (Pro tier at scale):

Gemini API cost per analysis: ~$0.03-0.08 (Flash pricing)
Tavily cost per analysis: ~$0.01-0.02
Margin at $149/month with ~30 analyses/user/month: >95% gross margin
SLIDE 7: Tech Stack + What's Next
Header: Built With + Roadmap

Tech Stack (with hackathon-relevant emphasis):

Component	Technology	Why
Primary AI	Google Gemini 2.0 Flash (Google AI Studio)	Best latency/cost for structured JSON generation. Multi-agent coordination needs fast, reliable inference.
Failover AI	NVIDIA NIM (Llama 3.3 70B)	Resilience. If Gemini rate-limits during live demo, system auto-switches without user knowing.
Real-Time Search	Tavily API	Grounds AI in current events. Without this, risks would be stale training-data hallucinations.
Financial Data	yfinance	Live prices, fundamentals, FX rates for 60+ global exchanges.
Frontend	Streamlit	Rapid iteration. Single Python file. Deploy in minutes.
Visualization	Plotly	Interactive maps (Scattermapbox), waterfall charts, dark-theme native.
Deployment	Streamlit Cloud (or local)	Zero infrastructure management.
Hackathon Resources Used:

Google AI Studio + Gemini 2.0 Flash API (primary intelligence engine)
Multi-agent architecture (5 coordinated agents)
Structured output / JSON mode for reliable parsing
Temperature tuning per agent role (0.3-0.6 range)
Roadmap (Next 3-6 months):

 SEC EDGAR 10-K Item 1A deep parsing (automated risk extraction from filings)
 SEBI/BSE filing integration for Indian equities
 Portfolio-level analysis (correlations across holdings)
 PDF export: McKinsey-style Investment Committee memo
 "Lying Gap" detection: news sentiment vs. filing language divergence = alpha signal
 Macro feedback loops: Chaos > 0.8 auto-adjusts simulated VIX/Oil
 Slack/Teams webhook alerts when new risks emerge for watchlist stocks
Closing line: > "The next crisis won't look like the last one. Project Doomsday doesn't predict which domino falls — it maps every domino, debates which ones are unstable, and calculates what happens when they all fall at once."