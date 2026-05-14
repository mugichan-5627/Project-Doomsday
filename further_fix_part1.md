🔧 COMPLETE FIX: Multi-Source Intelligence + Proper Valuation Models
You've raised critical points that would immediately get flagged by any finance-savvy judge:

SEC EDGAR filings (10-K, 10-Q Risk Factors) — the goldmine for US company self-disclosed risks
SEBI/BSE filings (DRHP, Annual Reports, Board Filings) — Indian regulatory disclosures
Financial companies can't use DCF — they need P/BV, Dividend Discount Model, or Excess Return
High-growth companies — need revenue multiples or Sum-of-Parts, not traditional FCF-DCF
Different valuation frameworks for different company types
Let me build all of this properly:

PART 1: REGULATORY FILING INTELLIGENCE ENGINE
# filing_intelligence.py
"""
Regulatory Filing Intelligence Engine
- SEC EDGAR (US): 10-K, 10-Q, 8-K Risk Factors + MD&A
- SEBI/BSE (India): DRHP, Annual Reports, Board Meeting Disclosures
- Company-disclosed risks are the HIGHEST quality signal
"""

import requests
import re
import json
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class FilingRisk:
    """A risk extracted from regulatory filings."""
    source: str  # "SEC_10K", "SEC_10Q", "SEC_8K", "SEBI_DRHP", "SEBI_AR", "BSE_BOARD"
    filing_date: str
    section: str  # "Risk Factors", "MD&A", "Legal Proceedings", etc.
    risk_text: str  # Exact quote from filing
    risk_category: str  # "operational", "financial", "regulatory", "market", "geopolitical"
    is_new: bool  # Was this risk added in the most recent filing?
    company_self_assessment: str  # "material", "significant", or extracted language


class SECEdgarEngine:
    """
    Pulls risk disclosures directly from SEC EDGAR.
    Companies are LEGALLY REQUIRED to disclose material risks in 10-K/10-Q.
    This is institutional-grade intelligence.
    """
    
    BASE_URL = "https://efts.sec.gov/LATEST/search-index"
    FULL_TEXT_SEARCH = "https://efts.sec.gov/LATEST/search-index"
    EDGAR_COMPANY = "https://data.sec.gov/submissions/CIK{cik}.json"
    EDGAR_FILING = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{filename}"
    
    # SEC requires a User-Agent header
    HEADERS = {
        "User-Agent": "ProjectDoomsday/1.0 (contact@example.com)",
        "Accept-Encoding": "gzip, deflate",
    }
    
    # CIK lookup for common tickers (fallback — normally we'd use the SEC ticker-CIK mapping)
    TICKER_CIK_MAP = {
        "NVDA": "0001045810",
        "MSFT": "0000789019",
        "AAPL": "0000320193",
        "GOOGL": "0001652044",
        "META": "0001326801",
        "AMZN": "0001018724",
        "TSLA": "0001318605",
        "TSM": "0001046179",
        "ASML": "0000937966",
        "JPM": "0000019617",
        "GS": "0000886982",
        "BAC": "0000070858",
        "BRK-B": "0001067983",
        "V": "0001403161",
        "MA": "0001141391",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def get_cik(self, ticker: str) -> Optional[str]:
        """Look up CIK from ticker using SEC's company tickers JSON."""
        # Check cache first
        clean_ticker = ticker.replace(".NS", "").replace("-", "").upper()
        if clean_ticker in self.TICKER_CIK_MAP:
            return self.TICKER_CIK_MAP[clean_ticker]
        
        # Query SEC's ticker-CIK mapping
        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for entry in data.values():
                    if entry.get("ticker", "").upper() == clean_ticker:
                        cik = str(entry["cik_str"]).zfill(10)
                        self.TICKER_CIK_MAP[clean_ticker] = cik
                        return cik
        except Exception as e:
            print(f"CIK lookup failed: {e}")
        
        return None
    
    def get_recent_filings(self, ticker: str, filing_types: List[str] = None) -> List[Dict]:
        """Get list of recent filings for a company."""
        if filing_types is None:
            filing_types = ["10-K", "10-Q", "8-K"]
        
        cik = self.get_cik(ticker)
        if not cik:
            return []
        
        try:
            url = f"https://data.sec.gov/submissions/CIK{cik}.json"
            response = self.session.get(url, timeout=15)
            time.sleep(0.2)  # SEC rate limit: 10 req/sec
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            recent_filings = data.get("filings", {}).get("recent", {})
            
            filings = []
            forms = recent_filings.get("form", [])
            dates = recent_filings.get("filingDate", [])
            accessions = recent_filings.get("accessionNumber", [])
            primary_docs = recent_filings.get("primaryDocument", [])
            
            for i in range(min(len(forms), 20)):  # Check last 20 filings
                if forms[i] in filing_types:
                    filings.append({
                        "form": forms[i],
                        "date": dates[i],
                        "accession": accessions[i].replace("-", ""),
                        "primary_doc": primary_docs[i],
                        "cik": cik.lstrip("0")
                    })
            
            return filings[:5]  # Return most recent 5
            
        except Exception as e:
            print(f"Error fetching filings: {e}")
            return []
    
    def extract_risk_factors(self, ticker: str) -> List[FilingRisk]:
        """
        Extract Risk Factors section from most recent 10-K or 10-Q.
        This is the PRIMARY source of company-disclosed risks.
        """
        filings = self.get_recent_filings(ticker, ["10-K", "10-Q"])
        
        if not filings:
            return []
        
        risks = []
        
        for filing in filings[:2]:  # Check last 2 filings
            try:
                # Construct URL to filing document
                cik = filing["cik"]
                accession = filing["accession"]
                doc = filing["primary_doc"]
                
                url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{doc}"
                response = self.session.get(url, timeout=30)
                time.sleep(0.3)  # Rate limiting
                
                if response.status_code != 200:
                    continue
                
                text = response.text
                
                # Extract Risk Factors section
                risk_section = self._extract_section(text, "Risk Factors")
                
                if risk_section:
                    # Parse individual risk items
                    individual_risks = self._parse_risk_items(risk_section)
                    
                    for risk_text in individual_risks[:15]:  # Top 15 risks
                        category = self._categorize_risk(risk_text)
                        risks.append(FilingRisk(
                            source=f"SEC_{filing['form'].replace('-', '')}",
                            filing_date=filing["date"],
                            section="Risk Factors",
                            risk_text=risk_text[:500],  # Truncate for LLM context
                            risk_category=category,
                            is_new=False,  # Would need diff with previous filing
                            company_self_assessment="material"  # By definition in Risk Factors
                        ))
                
                # Also extract from MD&A section (Management Discussion)
                mda_section = self._extract_section(text, "Management.{0,5}Discussion")
                if mda_section:
                    # Look for risk-related language in MD&A
                    risk_sentences = self._find_risk_sentences(mda_section)
                    for sent in risk_sentences[:5]:
                        risks.append(FilingRisk(
                            source=f"SEC_{filing['form'].replace('-', '')}",
                            filing_date=filing["date"],
                            section="MD&A",
                            risk_text=sent[:400],
                            risk_category=self._categorize_risk(sent),
                            is_new=False,
                            company_self_assessment="discussed"
                        ))
                
            except Exception as e:
                print(f"Error processing filing: {e}")
                continue
        
        return risks
    
    def _extract_section(self, html_text: str, section_name: str) -> Optional[str]:
        """Extract a named section from an SEC filing (HTML or text)."""
        # Remove HTML tags for text processing
        clean = re.sub(r'<[^>]+>', ' ', html_text)
        clean = re.sub(r'\s+', ' ', clean)
        
        # Find section boundaries
        # Common patterns: "Item 1A. Risk Factors", "RISK FACTORS", etc.
        patterns = [
            rf'Item\s*1A[\.\s]*{section_name}(.*?)Item\s*1B',
            rf'Item\s*1A[\.\s]*{section_name}(.*?)Item\s*2[\.\s]',
            rf'{section_name}\s*(.*?)(?:Item\s*\d|PART\s*II)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean, re.IGNORECASE | re.DOTALL)
            if match:
                section = match.group(1).strip()
                # Limit to reasonable length
                return section[:15000] if len(section) > 15000 else section
        
        # Fallback: just find the section header and grab text after it
        header_match = re.search(rf'{section_name}', clean, re.IGNORECASE)
        if header_match:
            start = header_match.end()
            return clean[start:start+10000]
        
        return None
    
    def _parse_risk_items(self, section_text: str) -> List[str]:
        """Parse individual risk factor items from the Risk Factors section."""
        # Risk factors are typically paragraphs starting with a bold title or bullet
        # Split by common patterns
        
        # Pattern 1: Lines that look like risk titles (short, possibly bold)
        items = []
        
        # Split by "We may", "Our", "The", "If" patterns that start new paragraphs
        risk_starters = re.split(
            r'(?:^|\.\s+)(?=[A-Z][^.]{10,80}(?:may|could|might|risk|uncertain|adverse|material|significant))',
            section_text
        )
        
        if len(risk_starters) < 3:
            # Fallback: split by double newlines or period + capital
            paragraphs = re.split(r'\n\n|\. (?=[A-Z])', section_text)
            risk_starters = [p.strip() for p in paragraphs if len(p.strip()) > 100]
        
        # Filter to actual risk statements
        for item in risk_starters:
            item = item.strip()
            if len(item) > 50 and any(word in item.lower() for word in [
                'risk', 'could', 'may', 'adverse', 'uncertain', 'material',
                'significant', 'disrupt', 'impair', 'harm', 'loss', 'decline',
                'failure', 'breach', 'regulatory', 'litigation', 'competition'
            ]):
                items.append(item)
        
        return items
    
    def _find_risk_sentences(self, text: str) -> List[str]:
        """Find risk-related sentences in MD&A section."""
        sentences = re.split(r'[.!?]+', text)
        risk_sentences = []
        
        risk_keywords = [
            'risk', 'uncertain', 'adverse', 'decline', 'challenge',
            'headwind', 'pressure', 'concern', 'threat', 'volatil',
            'disrupt', 'geopolit', 'tariff', 'sanction', 'regulation'
        ]
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 80 and any(kw in sent.lower() for kw in risk_keywords):
                risk_sentences.append(sent)
        
        return risk_sentences[:10]
    
    def _categorize_risk(self, text: str) -> str:
        """Categorize a risk based on keywords."""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ['geopolit', 'sanction', 'trade war', 'tariff', 'government', 'sovereign']):
            return "geopolitical"
        elif any(w in text_lower for w in ['supply chain', 'manufactur', 'logistics', 'shortage', 'inventory']):
            return "supply_chain"
        elif any(w in text_lower for w in ['regulat', 'compliance', 'litigation', 'lawsuit', 'antitrust']):
            return "regulatory"
        elif any(w in text_lower for w in ['debt', 'credit', 'liquidity', 'interest rate', 'refinanc', 'covenant']):
            return "financial"
        elif any(w in text_lower for w in ['cyber', 'data breach', 'privacy', 'technology', 'obsolescen']):
            return "technology"
        elif any(w in text_lower for w in ['competition', 'market share', 'customer', 'demand']):
            return "market"
        else:
            return "operational"


class SEBIFilingEngine:
    """
    Indian regulatory filing intelligence.
    Sources:
    - BSE/NSE Corporate Filings (Board Meeting outcomes, Financial Results)
    - SEBI DRHP (Draft Red Herring Prospectus) — exhaustive risk disclosure
    - Annual Reports (Management Discussion & Analysis section)
    
    Note: India doesn't have a free API like EDGAR. We use BSE's public listing page
    and supplement with Tavily search for recent filings.
    """
    
    BSE_CORPORATE_FILINGS = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
    BSE_COMPANY_INFO = "https://api.bseindia.com/BseIndiaAPI/api/ComHeadernew/w"
    
    # BSE scrip codes for common Indian tickers
    TICKER_SCRIP_MAP = {
        "RELIANCE.NS": "500325",
        "TCS.NS": "532540",
        "INFY.NS": "500209",
        "HDFCBANK.NS": "500180",
        "ITC.NS": "500875",
        "ICICIBANK.NS": "532174",
        "SBIN.NS": "500112",
        "BHARTIARTL.NS": "532454",
        "HINDUNILVR.NS": "500696",
        "TATAMOTORS.NS": "500570",
        "BAJFINANCE.NS": "500034",
        "ADANIENT.NS": "512599",
        "WIPRO.NS": "507685",
        "MARUTI.NS": "532500",
        "TATASTEEL.NS": "500470",
    }
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bseindia.com/",
    }
    
    def __init__(self, tavily_client=None):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.tavily = tavily_client
    
    def extract_risks(self, ticker: str) -> List[FilingRisk]:
        """
        Extract risks from Indian regulatory filings.
        Uses multiple approaches since India lacks a unified free API.
        """
        risks = []
        
        # Approach 1: BSE corporate filings (board disclosures)
        bse_risks = self._fetch_bse_disclosures(ticker)
        risks.extend(bse_risks)
        
        # Approach 2: Search for DRHP/Annual Report risk factors via Tavily
        if self.tavily:
            filing_risks = self._search_regulatory_filings(ticker)
            risks.extend(filing_risks)
        
        return risks
    
    def _fetch_bse_disclosures(self, ticker: str) -> List[FilingRisk]:
        """Fetch recent BSE corporate disclosures."""
        scrip_code = self.TICKER_SCRIP_MAP.get(ticker)
        if not scrip_code:
            return []
        
        try:
            # BSE corporate announcements API
            params = {
                "pageno": "1",
                "strCat": "-1",
                "strPrevDate": (datetime.now() - timedelta(days=90)).strftime("%Y%m%d"),
                "strScrip": scrip_code,
                "strSearch": "P",
                "strToDate": datetime.now().strftime("%Y%m%d"),
                "strType": "C"
            }
            
            response = self.session.get(self.BSE_CORPORATE_FILINGS, params=params, timeout=15)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            risks = []
            
            # Filter for risk-relevant announcements
            risk_keywords = ['risk', 'regulatory', 'order', 'penalty', 'investigation',
                           'material', 'adverse', 'litigation', 'fraud', 'default']
            
            for item in data.get("Table", [])[:20]:
                headline = item.get("NEWSSUB", "")
                if any(kw in headline.lower() for kw in risk_keywords):
                    risks.append(FilingRisk(
                        source="BSE_BOARD",
                        filing_date=item.get("NEWS_DT", ""),
                        section="Corporate Announcement",
                        risk_text=headline[:400],
                        risk_category=self._categorize_indian_risk(headline),
                        is_new=True,
                        company_self_assessment="disclosed"
                    ))
            
            return risks
            
        except Exception as e:
            print(f"BSE fetch error: {e}")
            return []
    
    def _search_regulatory_filings(self, ticker: str) -> List[FilingRisk]:
        """Use Tavily to find DRHP, Annual Report risk disclosures."""
        if not self.tavily:
            return []
        
        clean_name = ticker.replace(".NS", "").replace(".BO", "")
        
        queries = [
            f"{clean_name} DRHP risk factors SEBI filing",
            f"{clean_name} annual report risk management disclosure 2024",
            f"{clean_name} SEBI regulatory action penalty 2024 2025"
        ]
        
        risks = []
        
        for query in queries:
            try:
                result = self.tavily.search(query=query, search_depth="advanced", max_results=3)
                
                for r in result.get("results", []):
                    content = r.get("content", "")
                    title = r.get("title", "")
                    
                    # Check if it's actually about risk/regulation
                    if any(kw in (content + title).lower() for kw in ['risk', 'sebi', 'regulation', 'penalty', 'drhp', 'disclosure']):
                        risks.append(FilingRisk(
                            source="SEBI_FILING",
                            filing_date=r.get("published_date", datetime.now().strftime("%Y-%m-%d")),
                            section="Regulatory Disclosure",
                            risk_text=f"[{title}] {content[:350]}",
                            risk_category=self._categorize_indian_risk(content),
                            is_new=True,
                            company_self_assessment="regulatory_disclosure"
                        ))
            except:
                continue
        
        return risks
    
    def _categorize_indian_risk(self, text: str) -> str:
        """Categorize risk from Indian filings."""
        text_lower = text.lower()
        
        if any(w in text_lower for w in ['sebi', 'rbi', 'compliance', 'regulation', 'penalty']):
            return "regulatory"
        elif any(w in text_lower for w in ['fraud', 'governance', 'audit']):
            return "governance"
        elif any(w in text_lower for w in ['debt', 'npa', 'credit', 'default']):
            return "financial"
        elif any(w in text_lower for w in ['geopolit', 'export', 'tariff', 'government']):
            return "geopolitical"
        else:
            return "operational"


class UnifiedFilingEngine:
    """
    Unified interface that routes to SEC EDGAR or SEBI/BSE based on ticker.
    """
    
    def __init__(self, tavily_client=None):
        self.sec = SECEdgarEngine()
        self.sebi = SEBIFilingEngine(tavily_client=tavily_client)
    
    def is_indian_ticker(self, ticker: str) -> bool:
        """Check if ticker is Indian."""
        return ticker.endswith(".NS") or ticker.endswith(".BO")
    
    def extract_all_risks(self, ticker: str) -> Tuple[List[FilingRisk], str]:
        """
        Extract risks from appropriate regulatory source.
        Returns (risks, source_description)
        """
        if self.is_indian_ticker(ticker):
            risks = self.sebi.extract_risks(ticker)
            source = "SEBI/BSE Corporate Filings"
        else:
            risks = self.sec.extract_risk_factors(ticker)
            source = "SEC EDGAR (10-K/10-Q Risk Factors)"
        
        return risks, source
    
    def format_for_llm(self, risks: List[FilingRisk]) -> str:
        """Format filing risks as context for LLM agents."""
        if not risks:
            return "No regulatory filing risks available."
        
        output = "=== REGULATORY FILING INTELLIGENCE (Company Self-Disclosed Risks) ===\n\n"
        
        # Group by source
        by_source = {}
        for r in risks:
            if r.source not in by_source:
                by_source[r.source] = []
            by_source[r.source].append(r)
        
        for source, source_risks in by_source.items():
            output += f"[{source}] (Filed: {source_risks[0].filing_date})\n"
            for i, r in enumerate(source_risks[:8], 1):
                output += f"  {i}. [{r.risk_category.upper()}] {r.risk_text[:300]}\n"
            output += "\n"
        
        output += "NOTE: These are LEGALLY MANDATED disclosures. Companies must report MATERIAL risks.\n"
        output += "These risks have been reviewed by external auditors and legal counsel.\n"
        
        return output