"""Data fetching module using yfinance"""
import yfinance as yf
import pandas as pd
from datetime import datetime
import os
import pickle

class DataFetcher:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def fetch_stock_data(self, symbol, start_date, end_date, interval="1d", market="NSE"):
        """
        Fetch stock data from yfinance
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE') or index (e.g., '^NSEI')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
            market: NSE or BSE (ignored for indices starting with ^)
        
        Returns:
            DataFrame with OHLCV data
        """
        # Add market suffix only if not an index
        if symbol.startswith("^") or market == "":
            ticker = symbol
        else:
            suffix = ".NS" if market == "NSE" else ".BO"
            ticker = f"{symbol}{suffix}"
        
        # Check cache
        cache_file = self._get_cache_filename(ticker, start_date, end_date, interval)
        if os.path.exists(cache_file):
            print(f"Loading {ticker} from cache...")
            return pd.read_pickle(cache_file)
        
        # Fetch from yfinance
        print(f"Fetching {ticker} from yfinance...")
        try:
            data = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)
            
            if data.empty:
                raise ValueError(f"No data found for {ticker}")
            
            # Clean column names
            data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
            data.columns = data.columns.str.capitalize()
            
            # Save to cache
            data.to_pickle(cache_file)
            print(f"Cached data for {ticker}")
            
            return data
        
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return pd.DataFrame()
    
    def fetch_multiple_stocks(self, symbols, start_date, end_date, interval="1d", market="NSE"):
        """Fetch data for multiple stocks"""
        data_dict = {}
        for symbol in symbols:
            data = self.fetch_stock_data(symbol, start_date, end_date, interval, market)
            if not data.empty:
                data_dict[symbol] = data
        return data_dict
    
    def _get_cache_filename(self, ticker, start_date, end_date, interval):
        """Generate cache filename"""
        filename = f"{ticker}_{start_date}_{end_date}_{interval}.pkl"
        return os.path.join(self.cache_dir, filename)
    
    def clear_cache(self):
        """Clear all cached data"""
        for file in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, file))
        print("Cache cleared")
