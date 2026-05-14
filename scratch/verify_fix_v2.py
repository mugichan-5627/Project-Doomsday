import yfinance as yf
import time

def test_fetch(ticker):
    print(f"Testing {ticker}...")
    stock = yf.Ticker(ticker)
    
    # Simulate the helper logic
    info = {}
    try:
        info = stock.info
        if info and info.get("marketCap", 0) > 0:
            print(f"SUCCESS (info): {info.get('longName')}, MCap={info.get('marketCap')}")
            return
    except:
        pass
        
    print("info failed, trying fast_info...")
    try:
        fi = stock.fast_info
        if fi and fi.get("marketCap", 0) > 0:
            print(f"SUCCESS (fast_info): MCap={fi.get('marketCap')}, Price={fi.get('lastPrice')}")
            return
    except:
        pass
        
    print(f"FAILED for {ticker}")

if __name__ == "__main__":
    test_fetch("NVDA")
    test_fetch("RELIANCE.NS")
