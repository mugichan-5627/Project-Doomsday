
I need you to do the following tasks in TWO PHASES. Do Phase 1 now. Do NOT do Phase 2 until I explicitly say "deploy to github" or "go ahead with github".

=== PHASE 1: SIDEBAR API KEY INPUTS + STREAMLIT DEPLOYMENT PREP ===

DO NOT modify any existing logic, calculations, visuals, CSS, fonts, colors, or architecture. The ONLY code change is adding two password input fields in the sidebar and the corresponding key-override logic.

--- STEP 1: Add sidebar inputs ---

In app.py, in the sidebar section (inside `with st.sidebar:`), AFTER the chaos slider and chaos level visual indicator, and BEFORE the "LAUNCH ANALYSIS" button, add:

1. A horizontal divider (st.markdown("---"))

2. A section header in the existing style:
   st.markdown('API Keys', unsafe_allow_html=True)

3. Two text inputs with type="password":

   First input:
   - Label: "LLM API Key"
   - placeholder: "Google AI Studio, NVIDIA NIM, or Fireworks key"
   - type: password (shows dots)
   - Store value in st.session_state.user_llm_key

   Second input:
   - Label: "Tavily API Key"
   - placeholder: "Get key at tavily.com"
   - type: password (shows dots)
   - Store value in st.session_state.user_tavily_key

4. Below the inputs, add a small helper text in gray monospace (using the existing styling patterns):
   "Keys stay in your browser. Not stored."
   And on next line:
   "Get free keys: ai.google.dev | build.nvidia.com | fireworks.ai | tavily.com"

--- STEP 2: Key detection and override logic ---

Add a function (place it near the top, after the env loading section):

def apply_user_keys():
    """Override env keys with user-provided sidebar keys if present."""
    llm_key = st.session_state.get('user_llm_key', '').strip()
    tavily_key = st.session_state.get('user_tavily_key', '').strip()
    
    if llm_key:
        if llm_key.startswith("AIzaSy"):
            os.environ["GOOGLE_API_KEY"] = llm_key
        elif llm_key.startswith("nvapi-"):
            os.environ["NVIDIA_API_KEY"] = llm_key
        elif llm_key.startswith("fw_"):
            os.environ["FIREWORKS_API_KEY"] = llm_key
        else:
            # Default: try as Google key (most common for hackathon participants)
            os.environ["GOOGLE_API_KEY"] = llm_key
    
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key

Call apply_user_keys() at the very beginning of the `if launch:` block (the analysis pipeline), BEFORE the AI initialization step.

--- STEP 3: Handle missing keys gracefully ---

In the `if launch:` block, right after apply_user_keys() is called and BEFORE the AI initialization, add:

    # Check if any LLM key is available
    has_llm = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("NVIDIA_API_KEY") or os.getenv("FIREWORKS_API_KEY"))
    has_tavily = bool(os.getenv("TAVILY_API_KEY"))
    
    if not has_llm:
        st.error("No LLM API key found. Enter your key in the sidebar (Google AI Studio, NVIDIA NIM, or Fireworks).")
        st.stop()
    
    if not has_tavily:
        # Tavily is optional — analysis works without it (fallback risks)
        add_log("WARNING: No Tavily key. Using AI-only analysis (no live news search).", "warn")

--- STEP 4: Create deployment files ---

Create .streamlit/config.toml:
```toml
[theme]
primaryColor = "#ff3344"
backgroundColor = "#080b10"
secondaryBackgroundColor = "#0c1018"
textColor = "#c8d6e5"
font = "monospace"

[server]
headless = true
Ensure requirements.txt exists and contains:

streamlit>=1.28.0
plotly>=5.18.0
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.31
python-dotenv>=1.0.0
google-genai>=0.3.0
openai>=1.12.0
tavily-python>=0.3.0
--- STEP 5: Test locally ---

After making these changes, tell me you're done so I can test the app locally and verify:

The sidebar inputs appear correctly
The app works with keys entered in sidebar (no .env)
The app shows a clear error if no keys are provided
Nothing else has changed visually or functionally
DO NOT proceed to Phase 2 until I test and explicitly tell you to proceed.

How the key flow works:
User pastes key in sidebar → stored in st.session_state
                                    ↓
User clicks LAUNCH ANALYSIS → apply_user_keys() runs
                                    ↓
Key auto-detected by prefix:
  "AIzaSy..." → os.environ["GOOGLE_API_KEY"] = key
  "nvapi-..." → os.environ["NVIDIA_API_KEY"] = key
  "fw_..."   → os.environ["FIREWORKS_API_KEY"] = key
                                    ↓
DoomsdayAI.__init__() reads from os.environ (SAME as it does now)
                                    ↓
initialize() tries Gemini → NVIDIA → Fireworks (SAME failover chain)
                                    ↓
Works exactly like your local setup
Nothing in the connection logic changes. The DoomsdayAI class already reads keys from os.environ. All we're doing is putting the user's key INTO os.environ before the class reads it. From that point forward, it's identical to your local .env flow.

=== PHASE 2: GITHUB DEPLOYMENT (WAIT FOR MY GO-AHEAD) ===

DO NOT execute this phase until I explicitly say "deploy to github" or "go ahead" or "proceed with phase 2".

When I give the go-ahead:

Create .gitignore with:
.env
*.env
.env.*
.env.local
.env.production
__pycache__/
*.pyc
*.pyo
.streamlit/secrets.toml
venv/
.venv/
env/
*.log
.DS_Store
Thumbs.db
node_modules/
.idea/
.vscode/
*.swp
*.swo
Create README.md with:
# Project Doomsday

**Multi-Agent Black Swan Stress-Testing Engine**

An institutional-grade financial intelligence engine that stress-tests company valuations against global Black Swan events using a multi-agent AI swarm, adversarial debate architecture, and contagion propagation modeling.

## What It Does

Enter any stock ticker. In 60 seconds, the system:
- Deploys 5 AI agents across geopolitical, supply chain, financial, regulatory, and technology domains
- Runs adversarial Bear/Bull/Judge debates to validate each risk
- Maps threats geographically with convergence lines to company HQ
- Computes distressed valuations using 5-path methodology routing
- Models contagion cascades showing second/third-order propagation effects
- Displays full calculation transparency — no black boxes

## Tech Stack

- **AI Engine:** Google Gemini 2.0 Flash (with NVIDIA NIM / Fireworks AI failover)
- **Real-Time Search:** Tavily API
- **Financial Data:** yfinance
- **Frontend:** Streamlit
- **Visualization:** Plotly (maps, waterfall charts)
- **Markets Supported:** US, India (NSE/BSE), Global equities

## Setup

### Option 1: Use the deployed app
Visit the Streamlit deployment and enter your API keys directly in the sidebar.

### Option 2: Run locally
1. Clone this repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file:
GOOGLE_API_KEY=your_key_here TAVILY_API_KEY=your_key_here

4. Run: `streamlit run app.py`

### Getting API Keys (Free)
- **Google AI Studio (Gemini):** https://ai.google.dev
- **NVIDIA NIM:** https://build.nvidia.com
- **Fireworks AI:** https://fireworks.ai
- **Tavily:** https://tavily.com

## Features

- Multi-agent adversarial risk validation (Bear/Bull/Judge tribunal)
- 5-path valuation routing (Financial, High-Growth, Mature DCF, Cyclical, Fallback)
- Global fracture map with geographic vulnerability convergence
- Contagion cascade modeling (second/third/fourth-order effects)
- Real-time chaos slider (stress-test without re-running AI)
- Full valuation transparency panel (every formula, every number)
- Supports US + Indian + Global tickers with auto currency conversion

## Built For

Milan AI Week Hackathon 2025
Deployment order: a. git init (if needed) b. git add .gitignore AND commit it FIRST with message "Add .gitignore - protect sensitive files" c. Verify .env is NOT tracked: run git status and confirm .env does not appear d. git add app.py requirements.txt README.md .streamlit/config.toml e. Add any other .py files in the folder (valuation_engine.py, filing_intelligence.py if they exist) BUT NOT .env f. Commit with message "Project Doomsday v3.1 - Multi-Agent Black Swan Stress Engine" g. Push to GitHub repository named "Project-Doomsday"
SAFETY CHECKLIST before pushing:

 .gitignore is committed and contains .env
 git status does NOT show .env anywhere
 No file in staging contains any API key strings
 README tells users to bring their own keys
=== FINAL REMINDERS FOR BOTH PHASES ===

DO NOT change any existing CSS, fonts, colors, visual aesthetic
DO NOT change the map, waterfall chart, or any visualization
DO NOT change any calculation logic or valuation methodology
DO NOT add emojis anywhere in the code
DO NOT modify the adversarial debate system
DO NOT change the contagion cascade or transparency panel
The ONLY code modification is the sidebar key inputs + apply_user_keys() function + missing key check
Everything else is file creation (config, gitignore, readme)
WAIT for my explicit go-ahead before Phase 2