import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add backend to path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from mt5_bridge import mt5_bridge
from analysis_engine import analysis_engine

st.set_page_config(page_title="Algo Chart Tool", layout="wide", page_icon="📈")

# --- Sidebar ---
st.sidebar.title("Configuration")

# Connection Status
if mt5_bridge.connected:
    st.sidebar.success("MT5 Connected")
else:
    st.sidebar.error("MT5 Not Connected")
    if st.sidebar.button("Reconnect"):
        mt5_bridge._connect()
        st.experimental_rerun()

# Symbol Selection
symbol = st.sidebar.text_input("Symbol", value="EURUSD").upper()
timeframe_map = {
    "M1": 1, "M5": 5, "M15": 15, "M30": 30,
    "H1": 16385, "H4": 16388, "D1": 16408
}
timeframe_name = st.sidebar.selectbox("Timeframe", list(timeframe_map.keys()), index=4)
timeframe = timeframe_map[timeframe_name]

num_candles = st.sidebar.number_input("Number of Candles", min_value=100, max_value=5000, value=500)

# --- Main Content ---
st.title(f"{symbol} - {timeframe_name} Analysis")

# Fetch Data
@st.cache_data(ttl=1) # Cache for 1 second to allow near real-time updates on refresh
def load_data(sym, tf, n):
    return mt5_bridge.get_historical_data(sym, tf, n)

if mt5_bridge.connected:
    df = load_data(symbol, timeframe, num_candles)
    
    if df is not None and not df.empty:
        # --- Charting ---
        fig = go.Figure(data=[go.Candlestick(x=df['time'],
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name=symbol)])
        
        # Add Price Limits (Horizontal Lines)
        st.sidebar.subheader("Chart Overlays")
        limit_levels = st.sidebar.text_area("Price Limits (one per line)", height=100, help="Enter price levels to draw horizontal lines (e.g. Support/Resistance)")
        if limit_levels:
            for line in limit_levels.split('\n'):
                try:
                    price_level = float(line.strip())
                    fig.add_hline(y=price_level, line_dash="dash", line_color="yellow", annotation_text=f"Limit {price_level}")
                except ValueError:
                    pass

        # Add Buy/Sell Markers from Backtest
        if 'backtest_result' in st.session_state:
            res = st.session_state['backtest_result']
            if 'buy_signals' in res and res['buy_signals']['time']:
                fig.add_trace(go.Scatter(
                    x=res['buy_signals']['time'],
                    y=res['buy_signals']['price'],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=12, color='green'),
                    name='Buy Signal'
                ))
            if 'sell_signals' in res and res['sell_signals']['time']:
                fig.add_trace(go.Scatter(
                    x=res['sell_signals']['time'],
                    y=res['sell_signals']['price'],
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=12, color='red'),
                    name='Sell Signal'
                ))

        fig.update_layout(
            title=f"{symbol} Price Chart",
            yaxis_title="Price",
            xaxis_title="Time",
            height=600,
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # --- Analysis & Backtesting ---
        st.subheader("Strategy Lab")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Custom Strategy Script")
            st.markdown("""
            Define a function `generate_signals(df)` that returns a Series of:
            - `1` (Buy)
            - `-1` (Sell)
            - `0` (Hold)
            """)
            
            default_strategy = """
def generate_signals(df):
    # Example: Simple Moving Average Crossover
    # Calculate indicators using pandas-ta (available as 'df.ta')
    
    # Calculate SMA 20 and SMA 50
    sma_fast = df.ta.sma(length=20)
    sma_slow = df.ta.sma(length=50)
    
    # Generate signals
    signals = pd.Series(0, index=df.index)
    
    # Buy when Fast crosses above Slow
    signals[sma_fast > sma_slow] = 1
    
    # Sell when Fast crosses below Slow
    signals[sma_fast < sma_slow] = -1
    
    return signals
"""
            strategy_code = st.text_area("Python Code", value=default_strategy, height=300)
            
            if st.button("Run Backtest"):
                with st.spinner("Running Backtest..."):
                    result = analysis_engine.run_backtest(df, strategy_code)
                    
                    if "error" in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.session_state['backtest_result'] = result
                        st.success("Backtest Complete! Check chart for signals.")
                        st.rerun() # Rerun to update chart with markers

        with col2:
            st.markdown("### Results")
            if 'backtest_result' in st.session_state:
                res = st.session_state['backtest_result']
                st.metric("Total Return", f"{res['total_return']:.2%}")
                st.metric("Total Trades", res['trades'])
                
                # Plot Equity Curve
                equity_df = pd.DataFrame(res['equity_curve'], columns=['Equity'])
                st.line_chart(equity_df)
            else:
                st.info("Run a backtest to see results.")

    else:
        st.warning(f"No data found for {symbol}. Check if the symbol is valid and available in your MT5 Market Watch.")
else:
    st.warning("Please ensure MetaTrader 5 is running and try to reconnect.")

# Auto-refresh logic (optional, for "streaming" feel)
if st.sidebar.checkbox("Auto-Refresh (5s)"):
    st.rerun()
