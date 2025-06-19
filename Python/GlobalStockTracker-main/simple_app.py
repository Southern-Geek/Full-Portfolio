import streamlit as st
import yfinance as yf
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Global Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def format_currency(value):
    """Format a number as currency"""
    try:
        if value is None:
            return 'N/A'
        return f"${value:,.2f}"
    except:
        return 'N/A'

def format_percentage(value):
    """Format a number as percentage"""
    try:
        if value is None:
            return 'N/A'
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.2f}%"
    except:
        return 'N/A'

def get_stock_data(symbol):
    """Get current stock data"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if 'regularMarketPrice' in info:
            current_price = info.get('regularMarketPrice', 0)
            previous_close = info.get('previousClose', current_price)
        else:
            # Fallback to historical data
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                previous_close = hist['Close'].iloc[-2]
            else:
                return None
        
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
        
        return {
            'price': current_price,
            'change': change,
            'change_percent': change_percent,
            'volume': info.get('regularMarketVolume', 'N/A')
        }
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

# Sidebar configuration
st.sidebar.title("🌍 Global Markets")
st.sidebar.markdown("---")

# Auto-refresh settings
auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
refresh_interval = st.sidebar.selectbox(
    "Refresh Interval (seconds)",
    [30, 60, 120, 300],
    index=1
)

# Market selection
st.sidebar.subheader("Markets to Display")
available_indices = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC", 
    "Dow Jones": "^DJI",
    "FTSE 100": "^FTSE",
    "Nikkei 225": "^N225",
    "DAX": "^GDAXI",
    "CAC 40": "^FCHI",
    "Hang Seng": "^HSI",
    "Shanghai Composite": "000001.SS",
    "ASX 200": "^AXJO"
}

selected_indices = st.sidebar.multiselect(
    "Select Indices",
    list(available_indices.keys()),
    default=["S&P 500", "NASDAQ", "Dow Jones", "FTSE 100", "Nikkei 225"]
)

# Search functionality
st.sidebar.subheader("Search Stocks")
search_symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, GOOGL)")

# Main dashboard
st.title("📈 Global Stock Market Dashboard")
st.markdown("Real-time market data and interactive charts")

# Last update time
last_update_placeholder = st.empty()

# Create tabs
tab1, tab2 = st.tabs(["📊 Market Overview", "🔍 Stock Search"])

with tab1:
    st.header("Major Global Indices")
    
    if selected_indices:
        # Create progress bar for loading
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Fetch data for selected indices
        indices_data = []
        for i, index_name in enumerate(selected_indices):
            symbol = available_indices[index_name]
            status_text.text(f"Loading {index_name}...")
            
            data = get_stock_data(symbol)
            if data:
                indices_data.append({
                    'Index': index_name,
                    'Symbol': symbol,
                    'Price': data['price'],
                    'Change': data['change'],
                    'Change %': data['change_percent'],
                    'Volume': data.get('volume', 'N/A')
                })
            
            progress_bar.progress((i + 1) / len(selected_indices))
        
        progress_bar.empty()
        status_text.empty()
        
        if indices_data:
            # Display indices in cards
            cols = st.columns(min(3, len(indices_data)))
            
            for i, data in enumerate(indices_data):
                with cols[i % 3]:
                    st.metric(
                        label=f"{data['Index']}",
                        value=format_currency(data['Price']),
                        delta=f"{format_currency(data['Change'])} ({format_percentage(data['Change %'])})"
                    )
                    
                    st.caption(f"Volume: {data['Volume']}")
            
            # Create summary table
            st.subheader("Summary Table")
            
            # Format the data for display
            table_data = []
            for data in indices_data:
                table_data.append([
                    data['Index'],
                    format_currency(data['Price']),
                    format_currency(data['Change']),
                    format_percentage(data['Change %'])
                ])
            
            # Display as a simple table
            st.table(table_data)
    
    else:
        st.info("Please select at least one index from the sidebar to display market data.")

with tab2:
    st.header("Stock Search")
    
    if search_symbol:
        with st.spinner(f"Searching for {search_symbol.upper()}..."):
            stock_data = get_stock_data(search_symbol.upper())
            
        if stock_data:
            st.success(f"Found data for {search_symbol.upper()}")
            
            # Display stock information
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label=f"{search_symbol.upper()} Current Price",
                    value=format_currency(stock_data['price']),
                    delta=f"{format_currency(stock_data['change'])} ({format_percentage(stock_data['change_percent'])})"
                )
            
            with col2:
                if 'volume' in stock_data and stock_data['volume'] != 'N/A':
                    st.metric("Volume", f"{stock_data['volume']:,}")
        else:
            st.error(f"No data found for symbol: {search_symbol.upper()}")
    
    else:
        st.info("Enter a stock symbol in the sidebar to search for specific stock data.")
        
        # Popular stocks suggestions
        st.subheader("Popular Stocks")
        popular_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
        
        cols = st.columns(4)
        for i, stock in enumerate(popular_stocks):
            if cols[i % 4].button(stock):
                st.session_state.search_symbol = stock
                st.rerun()

# Auto-refresh functionality
if auto_refresh:
    last_update_placeholder.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh: {refresh_interval}s")
    
    # Auto-refresh after specified interval
    time.sleep(0.1)  # Small delay to prevent immediate refresh
    
    # Use JavaScript to refresh the page after the interval
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    if time.time() - st.session_state.last_refresh > refresh_interval:
        st.session_state.last_refresh = time.time()
        st.rerun()

else:
    last_update_placeholder.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh: Disabled")
    
    # Manual refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>📈 Global Stock Market Dashboard | Data provided by Yahoo Finance</p>
        <p><small>Disclaimer: This data is for informational purposes only and should not be considered as financial advice.</small></p>
    </div>
    """,
    unsafe_allow_html=True
)