import yfinance as yf
ticker = "NVDA"
stock = yf.Ticker(ticker)
try:
    print(f"FAST_INFO: {list(stock.fast_info.keys())}")
    print(f"MARKET CAP (FAST): {stock.fast_info.get('marketCap')}")
except Exception as e:
    print(f"ERROR FAST_INFO: {e}")
