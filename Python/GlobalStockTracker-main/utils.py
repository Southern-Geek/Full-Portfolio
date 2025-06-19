from datetime import datetime
import pytz
from typing import Dict, Any

def format_currency(value: float, currency: str = "USD") -> str:
    """
    Format a number as currency
    """
    try:
        if value is None or value == 'N/A':
            return 'N/A'
        
        # Handle very large numbers
        if abs(value) >= 1e12:
            return f"${value/1e12:.2f}T"
        elif abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        elif abs(value) >= 1000:
            return f"${value:,.2f}"
        else:
            return f"${value:.2f}"
    except (TypeError, ValueError):
        return 'N/A'

def format_percentage(value: float) -> str:
    """
    Format a number as percentage
    """
    try:
        if value is None or value == 'N/A':
            return 'N/A'
        
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.2f}%"
    except (TypeError, ValueError):
        return 'N/A'

def get_color_for_change(change: float) -> str:
    """
    Get color based on price change
    """
    try:
        if change > 0:
            return "green"
        elif change < 0:
            return "red"
        else:
            return "gray"
    except (TypeError, ValueError):
        return "gray"

def get_market_status(symbol: str) -> str:
    """
    Get market status based on symbol and current time
    This is a simplified version. In reality, you'd need more complex logic
    to handle different market hours for different exchanges.
    """
    try:
        now = datetime.now()
        current_hour = now.hour
        
        # Simplified market hours (US Eastern Time basis)
        # This is a basic implementation
        market_hours = {
            '^GSPC': (9, 16),  # S&P 500 (US)
            '^IXIC': (9, 16),  # NASDAQ (US)
            '^DJI': (9, 16),   # Dow Jones (US)
            '^FTSE': (8, 16),  # FTSE (UK)
            '^N225': (9, 15),  # Nikkei (Japan)
            '^GDAXI': (9, 17), # DAX (Germany)
            '^FCHI': (9, 17),  # CAC 40 (France)
            '^HSI': (9, 16),   # Hang Seng (Hong Kong)
            '000001.SS': (9, 15), # Shanghai
            '^AXJO': (10, 16)  # ASX (Australia)
        }
        
        if symbol in market_hours:
            open_hour, close_hour = market_hours[symbol]
            
            # Simple check - this would need timezone handling in reality
            if open_hour <= current_hour < close_hour:
                return "Open"
            else:
                return "Closed"
        
        return "Unknown"
        
    except Exception:
        return "Unknown"

def get_timezone_for_market(symbol: str) -> str:
    """
    Get timezone for different markets
    """
    market_timezones = {
        '^GSPC': 'US/Eastern',     # S&P 500
        '^IXIC': 'US/Eastern',     # NASDAQ
        '^DJI': 'US/Eastern',      # Dow Jones
        '^FTSE': 'Europe/London',  # FTSE 100
        '^N225': 'Asia/Tokyo',     # Nikkei 225
        '^GDAXI': 'Europe/Berlin', # DAX
        '^FCHI': 'Europe/Paris',   # CAC 40
        '^HSI': 'Asia/Hong_Kong',  # Hang Seng
        '000001.SS': 'Asia/Shanghai', # Shanghai Composite  
        '^AXJO': 'Australia/Sydney'   # ASX 200
    }
    
    return market_timezones.get(symbol, 'UTC')

def is_market_open(symbol: str) -> bool:
    """
    Check if a specific market is currently open
    """
    try:
        market_timezone = get_timezone_for_market(symbol)
        tz = pytz.timezone(market_timezone)
        local_time = datetime.now(tz)
        
        # Get current day of week (0 = Monday, 6 = Sunday)
        weekday = local_time.weekday()
        
        # Skip weekends
        if weekday >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        current_hour = local_time.hour
        
        # Market hours by exchange
        market_hours = {
            '^GSPC': (9, 16),      # NYSE: 9:30 AM - 4:00 PM ET
            '^IXIC': (9, 16),      # NASDAQ: 9:30 AM - 4:00 PM ET  
            '^DJI': (9, 16),       # NYSE: 9:30 AM - 4:00 PM ET
            '^FTSE': (8, 16),      # LSE: 8:00 AM - 4:30 PM GMT
            '^N225': (9, 15),      # TSE: 9:00 AM - 3:00 PM JST
            '^GDAXI': (9, 17),     # XETRA: 9:00 AM - 5:30 PM CET
            '^FCHI': (9, 17),      # Euronext: 9:00 AM - 5:30 PM CET
            '^HSI': (9, 16),       # HKEX: 9:30 AM - 4:00 PM HKT
            '000001.SS': (9, 15),  # SSE: 9:30 AM - 3:00 PM CST
            '^AXJO': (10, 16)      # ASX: 10:00 AM - 4:00 PM AEST
        }
        
        if symbol in market_hours:
            open_hour, close_hour = market_hours[symbol]
            return open_hour <= current_hour < close_hour
        
        return False
        
    except Exception:
        return False

def format_volume(volume) -> str:
    """
    Format trading volume in a readable way
    """
    try:
        if volume is None or volume == 'N/A':
            return 'N/A'
        
        volume = float(volume)
        
        if volume >= 1e9:
            return f"{volume/1e9:.1f}B"
        elif volume >= 1e6:
            return f"{volume/1e6:.1f}M"
        elif volume >= 1e3:
            return f"{volume/1e3:.1f}K"
        else:
            return f"{volume:,.0f}"
            
    except (TypeError, ValueError):
        return 'N/A'

def calculate_performance_metrics(historical_data) -> Dict[str, Any]:
    """
    Calculate various performance metrics from historical data
    """
    try:
        if historical_data is None or historical_data.empty:
            return {}
        
        close_prices = historical_data['Close']
        
        # Basic metrics
        current_price = close_prices.iloc[-1]
        start_price = close_prices.iloc[0]
        
        # Returns
        total_return = ((current_price - start_price) / start_price) * 100
        
        # Volatility (standard deviation of daily returns)
        daily_returns = close_prices.pct_change().dropna()
        volatility = daily_returns.std() * 100
        
        # High/Low
        period_high = historical_data['High'].max()
        period_low = historical_data['Low'].min()
        
        # Average volume
        avg_volume = historical_data['Volume'].mean()
        
        return {
            'total_return': total_return,
            'volatility': volatility,
            'period_high': period_high,
            'period_low': period_low,
            'avg_volume': avg_volume,
            'current_price': current_price,
            'start_price': start_price
        }
        
    except Exception as e:
        return {'error': str(e)}

def get_market_emoji(change_percent: float) -> str:
    """
    Get emoji based on market performance
    """
    try:
        if change_percent > 2:
            return "🚀"
        elif change_percent > 0:
            return "📈"
        elif change_percent > -2:
            return "📊"
        else:
            return "📉"
    except (TypeError, ValueError):
        return "📊"
