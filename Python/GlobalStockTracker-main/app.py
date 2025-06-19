import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import asyncio
from market_data import MarketDataProvider
from utils import format_currency, format_percentage, get_market_status, get_color_for_change

# Page configuration
st.set_page_config(
    page_title="Global Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize market data provider
@st.cache_resource
def get_market_provider():
    return MarketDataProvider()

market_provider = get_market_provider()

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
tab1, tab2, tab3 = st.tabs(["📊 Market Overview", "📈 Detailed Charts", "🔍 Stock Search"])

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
            
            try:
                data = market_provider.get_current_price(symbol)
                if data:
                    market_status = get_market_status(symbol)
                    indices_data.append({
                        'Index': index_name,
                        'Symbol': symbol,
                        'Price': data['price'],
                        'Change': data['change'],
                        'Change %': data['change_percent'],
                        'Volume': data.get('volume', 'N/A'),
                        'Market Status': market_status
                    })
            except Exception as e:
                st.error(f"Error loading {index_name}: {str(e)}")
            
            progress_bar.progress((i + 1) / len(selected_indices))
        
        progress_bar.empty()
        status_text.empty()
        
        if indices_data:
            # Display indices in cards
            cols = st.columns(min(3, len(indices_data)))
            
            for i, data in enumerate(indices_data):
                with cols[i % 3]:
                    change_color = get_color_for_change(data['Change'])
                    status_emoji = "🟢" if data['Market Status'] == "Open" else "🔴"
                    
                    st.metric(
                        label=f"{status_emoji} {data['Index']}",
                        value=format_currency(data['Price']),
                        delta=f"{format_currency(data['Change'])} ({format_percentage(data['Change %'])})"
                    )
                    
                    st.caption(f"Volume: {data['Volume']}")
                    st.caption(f"Status: {data['Market Status']}")
            
            # Create summary table
            st.subheader("Summary Table")
            df = pd.DataFrame(indices_data)
            
            # Format the dataframe for better display
            df_display = df.copy()
            df_display['Price'] = df_display['Price'].apply(format_currency)
            df_display['Change'] = df_display['Change'].apply(format_currency)
            df_display['Change %'] = df_display['Change %'].apply(format_percentage)
            
            st.dataframe(
                df_display[['Index', 'Price', 'Change', 'Change %', 'Market Status']],
                use_container_width=True,
                hide_index=True
            )
            
            # Market performance chart
            st.subheader("Daily Performance Comparison")
            fig = px.bar(
                df,
                x='Index',
                y='Change %',
                color='Change %',
                color_continuous_scale=['red', 'white', 'green'],
                title="Daily Change Percentage by Index"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("Please select at least one index from the sidebar to display market data.")

with tab2:
    st.header("Historical Charts")
    
    if selected_indices:
        chart_index = st.selectbox("Select Index for Detailed Chart", selected_indices)
        
        if chart_index:
            symbol = available_indices[chart_index]
            
            # Time range selection
            time_range = st.selectbox(
                "Select Time Range",
                ["1D", "5D", "1M", "3M", "6M", "1Y", "2Y", "5Y"],
                index=3
            )
            
            # Chart type selection
            chart_type = st.selectbox(
                "Chart Type",
                ["Line", "Candlestick", "OHLC"],
                index=0
            )
            
            try:
                with st.spinner(f"Loading historical data for {chart_index}..."):
                    historical_data = market_provider.get_historical_data(symbol, time_range)
                
                if historical_data is not None and not historical_data.empty:
                    fig = go.Figure()
                    
                    if chart_type == "Line":
                        fig.add_trace(go.Scatter(
                            x=historical_data.index,
                            y=historical_data['Close'],
                            mode='lines',
                            name='Close Price',
                            line=dict(color='blue', width=2)
                        ))
                    
                    elif chart_type == "Candlestick":
                        fig.add_trace(go.Candlestick(
                            x=historical_data.index,
                            open=historical_data['Open'],
                            high=historical_data['High'],
                            low=historical_data['Low'],
                            close=historical_data['Close'],
                            name=chart_index
                        ))
                    
                    elif chart_type == "OHLC":
                        fig.add_trace(go.Ohlc(
                            x=historical_data.index,
                            open=historical_data['Open'],
                            high=historical_data['High'],
                            low=historical_data['Low'],
                            close=historical_data['Close'],
                            name=chart_index
                        ))
                    
                    fig.update_layout(
                        title=f"{chart_index} - {time_range} Chart",
                        xaxis_title="Date",
                        yaxis_title="Price",
                        height=600,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display statistics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Period High", format_currency(historical_data['High'].max()))
                    with col2:
                        st.metric("Period Low", format_currency(historical_data['Low'].min()))
                    with col3:
                        current_price = historical_data['Close'].iloc[-1]
                        start_price = historical_data['Close'].iloc[0]
                        period_change = ((current_price - start_price) / start_price) * 100
                        st.metric("Period Change", format_percentage(period_change))
                    with col4:
                        avg_volume = historical_data['Volume'].mean()
                        st.metric("Avg Volume", f"{avg_volume:,.0f}")
                
                else:
                    st.error(f"No historical data available for {chart_index}")
                    
            except Exception as e:
                st.error(f"Error loading historical data: {str(e)}")
    
    else:
        st.info("Please select an index from the Market Overview tab to view detailed charts.")

with tab3:
    st.header("Stock Search")
    
    if search_symbol:
        try:
            with st.spinner(f"Searching for {search_symbol.upper()}..."):
                stock_data = market_provider.get_current_price(search_symbol.upper())
                
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
                    if 'volume' in stock_data:
                        st.metric("Volume", f"{stock_data['volume']:,}")
                
                # Get historical data for the searched stock
                time_range_search = st.selectbox(
                    "Time Range for Chart",
                    ["1D", "5D", "1M", "3M", "6M", "1Y"],
                    index=2,
                    key="search_time_range"
                )
                
                historical_search = market_provider.get_historical_data(search_symbol.upper(), time_range_search)
                
                if historical_search is not None and not historical_search.empty:
                    # Create line chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=historical_search.index,
                        y=historical_search['Close'],
                        mode='lines',
                        name=search_symbol.upper(),
                        line=dict(color='blue', width=2)
                    ))
                    
                    fig.update_layout(
                        title=f"{search_symbol.upper()} - {time_range_search} Price Chart",
                        xaxis_title="Date",
                        yaxis_title="Price",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.error(f"No data found for symbol: {search_symbol.upper()}")
                
        except Exception as e:
            st.error(f"Error searching for {search_symbol.upper()}: {str(e)}")
    
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
