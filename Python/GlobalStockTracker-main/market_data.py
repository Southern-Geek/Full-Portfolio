import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, Optional, Any
import time

class MarketDataProvider:
    """
    A class to handle all market data operations using yfinance
    """
    
    def __init__(self):
        self.cache_duration = 60  # Cache data for 60 seconds
        self.data_cache = {}
    
    def _is_cache_valid(self, symbol: str, data_type: str = "current") -> bool:
        """Check if cached data is still valid"""
        cache_key = f"{symbol}_{data_type}"
        if cache_key not in self.data_cache:
            return False
        
        cached_time = self.data_cache[cache_key].get('timestamp', 0)
        return (time.time() - cached_time) < self.cache_duration
    
    def _get_from_cache(self, symbol: str, data_type: str = "current") -> Optional[Any]:
        """Get data from cache if valid"""
        cache_key = f"{symbol}_{data_type}"
        if self._is_cache_valid(symbol, data_type):
            return self.data_cache[cache_key]['data']
        return None
    
    def _set_cache(self, symbol: str, data: Any, data_type: str = "current") -> None:
        """Set data in cache with timestamp"""
        cache_key = f"{symbol}_{data_type}"
        self.data_cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    @st.cache_data(ttl=60)
    def get_current_price(_self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get current price and basic info for a symbol
        """
        try:
            # Check cache first
            cached_data = _self._get_from_cache(symbol, "current")
            if cached_data:
                return cached_data
            
            ticker = yf.Ticker(symbol)
            
            # Get current data
            info = ticker.info
            
            if info and 'regularMarketPrice' in info:
                current_price = info.get('regularMarketPrice', 0)
                previous_close = info.get('previousClose', current_price)
                
                # Calculate change
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                
                data = {
                    'price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'volume': info.get('regularMarketVolume', 'N/A'),
                    'previous_close': previous_close,
                    'market_cap': info.get('marketCap', 'N/A'),
                    'currency': info.get('currency', 'USD')
                }
                
                # Cache the data
                _self._set_cache(symbol, data, "current")
                return data
            
            else:
                # Fallback: get data from history
                hist = ticker.history(period="2d")
                if not hist.empty and len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2]
                    
                    change = current_price - previous_price
                    change_percent = (change / previous_price) * 100 if previous_price != 0 else 0
                    
                    data = {
                        'price': current_price,
                        'change': change,
                        'change_percent': change_percent,
                        'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 'N/A',
                        'previous_close': previous_price,
                        'market_cap': 'N/A',
                        'currency': 'USD'
                    }
                    
                    # Cache the data
                    _self._set_cache(symbol, data, "current")
                    return data
                
                return None
                
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    @st.cache_data(ttl=300)  # Cache historical data for 5 minutes
    def get_historical_data(_self, symbol: str, period: str) -> Optional[pd.DataFrame]:
        """
        Get historical data for a symbol
        
        Parameters:
        symbol: Stock symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        """
        try:
            # Map period formats
            period_map = {
                "1D": "1d",
                "5D": "5d", 
                "1M": "1mo",
                "3M": "3mo",
                "6M": "6mo",
                "1Y": "1y",
                "2Y": "2y",
                "5Y": "5y"
            }
            
            yf_period = period_map.get(period, period.lower())
            
            ticker = yf.Ticker(symbol)
            
            # For very short periods, use interval parameter
            if yf_period in ["1d"]:
                hist = ticker.history(period=yf_period, interval="5m")
            elif yf_period in ["5d"]:
                hist = ticker.history(period=yf_period, interval="15m")
            else:
                hist = ticker.history(period=yf_period)
            
            if hist.empty:
                return None
            
            # Clean the data
            hist = hist.dropna()
            
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in hist.columns for col in required_columns):
                return None
            
            return hist
            
        except Exception as e:
            st.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def get_multiple_current_prices(self, symbols: list) -> Dict[str, Dict[str, Any]]:
        """
        Get current prices for multiple symbols efficiently
        """
        results = {}
        
        for symbol in symbols:
            try:
                data = self.get_current_price(symbol)
                if data:
                    results[symbol] = data
            except Exception as e:
                st.warning(f"Failed to fetch data for {symbol}: {str(e)}")
                continue
        
        return results
    
    def get_market_summary(self, symbols: list) -> pd.DataFrame:
        """
        Get a summary DataFrame for multiple symbols
        """
        data_list = []
        
        for symbol in symbols:
            try:
                data = self.get_current_price(symbol)
                if data:
                    data_list.append({
                        'Symbol': symbol,
                        'Price': data['price'],
                        'Change': data['change'],
                        'Change %': data['change_percent'],
                        'Volume': data.get('volume', 'N/A')
                    })
            except Exception as e:
                continue
        
        return pd.DataFrame(data_list) if data_list else pd.DataFrame()
    
    def search_symbol(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Search for a symbol and return basic info if found
        """
        try:
            # Clean the query
            query = query.strip().upper()
            
            # Try to get data for the symbol
            data = self.get_current_price(query)
            
            if data:
                return {
                    'symbol': query,
                    'found': True,
                    'data': data
                }
            else:
                return {
                    'symbol': query,
                    'found': False,
                    'data': None
                }
                
        except Exception as e:
            return {
                'symbol': query,
                'found': False,
                'error': str(e)
            }
