import requests
import yfinance as yf
import time
from typing import Optional

# Mocking parts of the app to test logic
def resolve_ticker(ticker):
    return ticker.upper()

def _get_info(stock_obj):
    """Internal helper to get info with retries and fallback."""
    inf = {}
    try:
        inf = stock_obj.info
        if inf and inf.get("marketCap", 0) > 0:
            return inf
    except:
        pass
    
    time.sleep(1)
    try:
        inf = stock_obj.info
        if inf and inf.get("marketCap", 0) > 0:
            return inf
    except:
        pass
        
    try:
        fi = stock_obj.fast_info
        if fi and fi.get("marketCap", 0) > 0:
            return {
                "marketCap": fi.get("marketCap"),
                "currentPrice": fi.get("lastPrice"),
                "sharesOutstanding": fi.get("shares"),
                "currency": fi.get("currency", "USD"),
            }
    except:
        pass
    return {}

def test_fetch(ticker):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    })
    
    resolved = resolve_ticker(ticker)
    stock = yf.Ticker(resolved, session=session)
    info = _get_info(stock)
    
    if not info or info.get("marketCap", 0) == 0:
        print(f"FAILED for {ticker}")
    else:
        print(f"SUCCESS for {ticker}: Name={info.get('longName', 'N/A')}, MCap={info.get('marketCap')}")

if __name__ == "__main__":
    test_fetch("NVDA")
    test_fetch("RELIANCE.NS")
