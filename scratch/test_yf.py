import yfinance as yf
import json

ticker = "NVDA"
stock = yf.Ticker(ticker)
try:
    info = stock.info
    print(f"Ticker: {ticker}")
    print(f"Name: {info.get('longName')}")
    print(f"Market Cap: {info.get('marketCap')}")
    print(f"Current Price: {info.get('currentPrice')}")
    
    if not info or info.get("marketCap", 0) == 0:
        print("FAILED: marketCap is 0 or info is empty")
    else:
        print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
