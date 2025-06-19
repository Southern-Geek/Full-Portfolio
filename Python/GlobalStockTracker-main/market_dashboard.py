import streamlit as st
import requests
import json
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

def get_yahoo_finance_data(symbol):
    """Get stock data using Yahoo Finance API"""
    try:
        # Use Yahoo Finance query API
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                meta = result['meta']
                
                current_price = meta.get('regularMarketPrice', 0)
                previous_close = meta.get('previousClose', current_price)
                
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100 if previous_close != 0 else 0
                
                return {
                    'symbol': symbol,
                    'price': current_price,
                    'change': change,
                    'change_percent': change_percent,
                    'volume': meta.get('regularMarketVolume', 'N/A'),
                    'currency': meta.get('currency', 'USD'),
                    'market_state': meta.get('marketState', 'UNKNOWN')
                }
        
        return None
        
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def get_market_status_emoji(market_state):
    """Get emoji based on market state"""
    if market_state == 'REGULAR':
        return "🟢"
    elif market_state == 'CLOSED':
        return "🔴"
    elif market_state == 'PRE':
        return "🟡"
    elif market_state == 'POST':
        return "🟠"
    else:
        return "⚪"

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
st.markdown("Real-time market data from Yahoo Finance")

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
            
            data = get_yahoo_finance_data(symbol)
            if data:
                indices_data.append({
                    'Index': index_name,
                    'Symbol': symbol,
                    'Price': data['price'],
                    'Change': data['change'],
                    'Change %': data['change_percent'],
                    'Volume': data.get('volume', 'N/A'),
                    'Market State': data.get('market_state', 'UNKNOWN')
                })
            
            progress_bar.progress((i + 1) / len(selected_indices))
        
        progress_bar.empty()
        status_text.empty()
        
        if indices_data:
            # Display indices in cards
            cols = st.columns(min(3, len(indices_data)))
            
            for i, data in enumerate(indices_data):
                with cols[i % 3]:
                    status_emoji = get_market_status_emoji(data['Market State'])
                    
                    st.metric(
                        label=f"{status_emoji} {data['Index']}",
                        value=format_currency(data['Price']),
                        delta=f"{format_currency(data['Change'])} ({format_percentage(data['Change %'])})"
                    )
                    
                    if data['Volume'] != 'N/A':
                        st.caption(f"Volume: {data['Volume']:,}")
                    else:
                        st.caption("Volume: N/A")
                    
                    st.caption(f"Status: {data['Market State']}")
            
            # Create summary table
            st.subheader("Summary Table")
            
            # Create table headers
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.write("**Index**")
            with col2:
                st.write("**Price**")
            with col3:
                st.write("**Change**")
            with col4:
                st.write("**Change %**")
            with col5:
                st.write("**Status**")
            
            # Add separator
            st.markdown("---")
            
            # Display data rows
            for data in indices_data:
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                with col1:
                    st.write(data['Index'])
                with col2:
                    st.write(format_currency(data['Price']))
                with col3:
                    st.write(format_currency(data['Change']))
                with col4:
                    color = "green" if data['Change %'] > 0 else "red" if data['Change %'] < 0 else "gray"
                    st.markdown(f"<span style='color: {color}'>{format_percentage(data['Change %'])}</span>", unsafe_allow_html=True)
                with col5:
                    emoji = get_market_status_emoji(data['Market State'])
                    st.write(f"{emoji} {data['Market State']}")
        else:
            st.warning("No data could be retrieved for the selected indices. Please try again later.")
    
    else:
        st.info("Please select at least one index from the sidebar to display market data.")

with tab2:
    st.header("Stock Search")
    
    if search_symbol:
        with st.spinner(f"Searching for {search_symbol.upper()}..."):
            stock_data = get_yahoo_finance_data(search_symbol.upper())
            
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
                if stock_data['volume'] != 'N/A':
                    st.metric("Volume", f"{stock_data['volume']:,}")
                else:
                    st.metric("Volume", "N/A")
            
            # Additional information
            st.subheader("Additional Information")
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.write(f"**Currency:** {stock_data.get('currency', 'USD')}")
            
            with info_col2:
                emoji = get_market_status_emoji(stock_data.get('market_state', 'UNKNOWN'))
                st.write(f"**Market Status:** {emoji} {stock_data.get('market_state', 'UNKNOWN')}")
                
        else:
            st.error(f"No data found for symbol: {search_symbol.upper()}")
            st.info("Please check the symbol and try again. Make sure to use the correct stock ticker symbol.")
    
    else:
        st.info("Enter a stock symbol in the sidebar to search for specific stock data.")
        
        # Popular stocks suggestions
        st.subheader("Popular Stocks")
        st.write("Click on any of these popular stocks to search:")
        
        popular_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX"]
        
        cols = st.columns(4)
        for i, stock in enumerate(popular_stocks):
            with cols[i % 4]:
                if st.button(stock, key=f"popular_{stock}"):
                    # Get data for the clicked stock
                    with st.spinner(f"Loading {stock}..."):
                        stock_data = get_yahoo_finance_data(stock)
                    
                    if stock_data:
                        st.metric(
                            label=f"{stock}",
                            value=format_currency(stock_data['price']),
                            delta=f"{format_percentage(stock_data['change_percent'])}"
                        )

# Auto-refresh functionality
if auto_refresh:
    last_update_placeholder.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refresh: {refresh_interval}s")
    
    # Auto-refresh after specified interval
    time.sleep(0.1)  # Small delay to prevent immediate refresh
    
    # Use session state to track refresh timing
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
        <p>📈 Global Stock Market Dashboard | Data provided by Yahoo Finance API</p>
        <p><small>Disclaimer: This data is for informational purposes only and should not be considered as financial advice.</small></p>
    </div>
    """,
    unsafe_allow_html=True
)