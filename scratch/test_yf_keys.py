import yfinance as yf
import json

ticker = "NVDA"
stock = yf.Ticker(ticker)
try:
    info = stock.info
    print(f"KEYS: {list(info.keys())}")
    print(f"MARKET CAP: {info.get('marketCap')}")
except Exception as e:
    print(f"ERROR: {e}")
