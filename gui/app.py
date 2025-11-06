"""Streamlit GUI for Hammer Pattern Backtester"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.data_fetcher import DataFetcher
from strategies.hammer_strategy import HammerStrategy
from strategies.shooting_star_strategy import ShootingStarStrategy
from strategies.ny_session_strategy import NYSessionStrategy
from backtester.engine import BacktestEngine
from config import Config

# Market symbols organized by category
MARKET_SYMBOLS = {
    "Indian Stocks": {
        "NIFTY 50": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "RELIANCE": "RELIANCE",
        "TCS": "TCS",
        "HDFC BANK": "HDFCBANK",
        "INFOSYS": "INFY",
        "ICICI BANK": "ICICIBANK",
        "BHARTI AIRTEL": "BHARTIARTL",
        "ITC": "ITC",
        "KOTAK BANK": "KOTAKBANK",
        "LT": "LT",
        "AXIS BANK": "AXISBANK",
        "HCL TECH": "HCLTECH",
        "MARUTI": "MARUTI",
        "SBI": "SBIN",
        "BAJAJ FINANCE": "BAJFINANCE",
        "ASIAN PAINTS": "ASIANPAINT",
        "TITAN": "TITAN",
        "WIPRO": "WIPRO",
        "TATA STEEL": "TATASTEEL",
        "ADANI PORTS": "ADANIPORTS",
        "POWER GRID": "POWERGRID",
        "NTPC": "NTPC",
        "ONGC": "ONGC",
        "COAL INDIA": "COALINDIA"
    },
    "Forex": {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "JPY=X",
        "USD/CHF": "CHF=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "CAD=X",
        "NZD/USD": "NZDUSD=X",
        "EUR/GBP": "EURGBP=X",
        "EUR/JPY": "EURJPY=X",
        "GBP/JPY": "GBPJPY=X",
        "USD/INR": "INR=X",
        "EUR/INR": "EURINR=X",
        "GBP/INR": "GBPINR=X"
    },
    "Crypto": {
        "BTC/USD - Bitcoin": "BTC-USD",
        "ETH/USD - Ethereum": "ETH-USD",
        "BNB/USD - Binance Coin": "BNB-USD",
        "ADA/USD - Cardano": "ADA-USD",
        "SOL/USD - Solana": "SOL-USD",
        "XRP/USD - Ripple": "XRP-USD",
        "DOT/USD - Polkadot": "DOT-USD",
        "DOGE/USD - Dogecoin": "DOGE-USD",
        "AVAX/USD - Avalanche": "AVAX-USD",
        "MATIC/USD - Polygon": "MATIC-USD",
        "LINK/USD - Chainlink": "LINK-USD",
        "LTC/USD - Litecoin": "LTC-USD",
        "BCH/USD - Bitcoin Cash": "BCH-USD",
        "XLM/USD - Stellar": "XLM-USD",
        "ATOM/USD - Cosmos": "ATOM-USD"
    },
    "Commodities": {
        "Gold (XAU/USD)": "GC=F",
        "Silver (XAG/USD)": "SI=F",
        "Crude Oil (WTI)": "CL=F",
        "Natural Gas": "NG=F"
    }
}

st.set_page_config(page_title="Hammer Pattern Backtester", layout="wide", page_icon="🔨")

def plot_candlestick_with_signals(df, trades_df, symbol):
    """Plot candlestick chart with entry/exit markers"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{symbol} - Price Action', 'Volume')
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price'
        ),
        row=1, col=1
    )
    
    # Mark hammer patterns
    if 'is_hammer' in df.columns:
        hammer_df = df[df['is_hammer'] == True]
        if not hammer_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=hammer_df.index,
                    y=hammer_df['Low'] * 0.995,
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=10, color='yellow'),
                    name='Hammer'
                ),
                row=1, col=1
            )
    
    # Mark shooting star patterns
    if 'is_shooting_star' in df.columns:
        shooting_star_df = df[df['is_shooting_star'] == True]
        if not shooting_star_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=shooting_star_df.index,
                    y=shooting_star_df['High'] * 1.005,
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=10, color='orange'),
                    name='Shooting Star'
                ),
                row=1, col=1
            )
    
    # Mark entry points
    if not trades_df.empty:
        fig.add_trace(
            go.Scatter(
                x=trades_df['entry_date'],
                y=trades_df['entry_price'],
                mode='markers',
                marker=dict(symbol='triangle-up', size=12, color='green'),
                name='Entry'
            ),
            row=1, col=1
        )
        
        # Mark exit points
        fig.add_trace(
            go.Scatter(
                x=trades_df['exit_date'],
                y=trades_df['exit_price'],
                mode='markers',
                marker=dict(symbol='triangle-down', size=12, color='red'),
                name='Exit'
            ),
            row=1, col=1
        )
    
    # Volume bars
    colors = ['red' if row['Close'] < row['Open'] else 'green' for _, row in df.iterrows()]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'),
        row=2, col=1
    )
    
    fig.update_layout(
        height=800,
        xaxis_rangeslider_visible=False,
        showlegend=True
    )
    
    return fig

def plot_equity_curve(equity_df):
    """Plot equity curve"""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=equity_df['date'],
            y=equity_df['equity'],
            mode='lines',
            name='Equity',
            line=dict(color='blue', width=2)
        )
    )
    
    fig.update_layout(
        title='Equity Curve',
        xaxis_title='Date',
        yaxis_title='Equity (Rs.)',
        height=400
    )
    
    return fig

def main():
    st.title("🔨 Reversal Pattern Backtester")
    st.markdown("**Strategies:** Hammer (LONG) | Shooting Star (SHORT)")
    st.markdown("**Markets:** Indian Stocks 🇮🇳 | Forex 💱 | Crypto ₿")
    st.info("ℹ️ All times displayed in IST (Indian Standard Time)")
    st.markdown("---")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Market selection
        st.subheader("🌍 Market Selection")
        
        market_type = st.selectbox(
            "Choose Market:",
            ["Indian Stocks", "Forex", "Crypto", "Commodities"]
        )
        
        # Symbol selection based on market
        input_method = st.radio(
            "Input Method:",
            ["Popular Symbols", "Custom Symbol"]
        )
        
        if input_method == "Popular Symbols":
            symbol_name = st.selectbox(
                f"Select {market_type}",
                list(MARKET_SYMBOLS[market_type].keys())
            )
            symbol = MARKET_SYMBOLS[market_type][symbol_name]
            
            # Determine market suffix
            if market_type == "Indian Stocks":
                market = "" if symbol.startswith("^") else "NSE"
            else:
                market = ""  # Forex and Crypto don't need market suffix
        else:
            if market_type == "Indian Stocks":
                symbol = st.text_input("Enter Symbol", value="RELIANCE", help="Enter stock symbol without .NS")
                market = st.selectbox("Exchange", ["NSE", "BSE"])
            elif market_type == "Forex":
                symbol = st.text_input("Enter Forex Pair", value="EURUSD=X", help="Format: EURUSD=X")
                market = ""
            else:  # Crypto
                symbol = st.text_input("Enter Crypto Symbol", value="BTC-USD", help="Format: BTC-USD")
                market = ""
        
        # Market-specific info
        if market_type == "Indian Stocks":
            st.caption("📊 NSE/BSE stocks | Market: 9:15 AM - 3:30 PM IST")
        elif market_type == "Forex":
            st.caption("💱 24/5 Market | Closed on weekends")
        else:
            st.caption("₿ 24/7 Market | Always open")
        
        # Timeframe selection
        st.markdown("---")
        st.subheader("📅 Timeframe")
        
        interval = st.selectbox(
            "Interval",
            ["5m", "15m", "30m", "1h", "1d", "1wk"],
            index=4,
            help="Note: Intraday data limited by yfinance"
        )
        
        # Date range based on interval
        if interval in ["5m", "15m", "30m"]:
            max_days = 55
            default_days = 55
            st.info("⚠️ Intraday data limited to last 60 days")
        elif interval == "1h":
            max_days = 730
            default_days = 180
        else:
            max_days = 3650
            default_days = 365
        
        days_back = st.slider(
            "Days of History",
            min_value=30,
            max_value=max_days,
            value=default_days,
            step=30
        )
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        st.text(f"From: {start_date.strftime('%Y-%m-%d')}")
        st.text(f"To: {end_date.strftime('%Y-%m-%d')}")
        
        # Capital settings
        st.markdown("---")
        st.subheader("💰 Capital Settings")
        
        initial_capital = st.number_input(
            "Initial Capital (Rs.)",
            min_value=10000,
            max_value=10000000,
            value=100000,
            step=10000
        )
        
        position_size = st.slider(
            "Position Size (%)",
            min_value=1,
            max_value=100,
            value=10,
            help="Percentage of capital to risk per trade"
        ) / 100
        
        # Strategy parameters
        st.markdown("---")
        st.subheader("📊 Strategy Selection")
        
        strategy_type = st.radio(
            "Choose Strategy:",
            ["Hammer (LONG)", "Shooting Star (SHORT)", "NY Session Breakout"]
        )
        
        if strategy_type == "NY Session Breakout":
            st.info("📍 NY Session: 8:00 AM - 12:00 PM EST (First 4 hours)")
            st.caption("Works best on 5-min timeframe for Gold, Crypto, Forex")
            trend_candles = 6  # Not used for NY strategy
        else:
            if strategy_type == "Hammer (LONG)":
                trend_label = "Downtrend Candles"
                trend_help = "Number of consecutive down candles (each not breaking previous high)"
            else:
                trend_label = "Uptrend Candles"
                trend_help = "Number of consecutive up candles (each not breaking previous low)"
            
            trend_candles = st.slider(
                trend_label,
                min_value=3,
                max_value=10,
                value=6,
                help=trend_help
            )
        
        risk_reward = st.slider(
            "Risk:Reward Ratio",
            min_value=1.0,
            max_value=3.0,
            value=1.5,
            step=0.1
        )
        
        st.markdown("---")
        run_backtest = st.button("🚀 Run Backtest", type="primary", use_container_width=True)
    
    # Main content
    if run_backtest:
        with st.spinner(f"Fetching data for {symbol}..."):
            # Fetch data
            fetcher = DataFetcher()
            
            market_param = "" if symbol.startswith("^") else market
            
            df = fetcher.fetch_stock_data(
                symbol,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                interval,
                market_param
            )
            
            if df.empty:
                st.error(f"❌ No data found for {symbol}. Please check the symbol and try again.")
                return
            
            st.success(f"✅ Fetched {len(df)} candles")
        
        with st.spinner("Running backtest..."):
            # Run backtest with selected strategy
            if strategy_type == "Hammer (LONG)":
                strategy = HammerStrategy(trend_candles, risk_reward)
            elif strategy_type == "Shooting Star (SHORT)":
                strategy = ShootingStarStrategy(trend_candles, risk_reward)
            else:  # NY Session Breakout
                strategy = NYSessionStrategy(session_start_hour=8, risk_reward=risk_reward)
            
            Config.MAX_POSITION_SIZE = position_size
            engine = BacktestEngine(strategy, initial_capital)
            results = engine.run(df, symbol)
        
        st.success("✅ Backtest completed!")
        
        # Display results
        st.header("📊 Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Return", f"{results['total_return']:.2f}%")
            st.metric("Total Trades", results['total_trades'])
        
        with col2:
            st.metric("Win Rate", f"{results['win_rate']:.2f}%")
            st.metric("Winning Trades", results['winning_trades'])
        
        with col3:
            st.metric("Total P&L", f"Rs.{results['total_pnl']:,.2f}")
            st.metric("Losing Trades", results['losing_trades'])
        
        with col4:
            st.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")
            if results['total_trades'] > 0:
                st.metric("Profit Factor", f"{results['profit_factor']:.2f}")
        
        st.markdown("---")
        
        # Charts
        if results['total_trades'] > 0:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📈 Price Chart with Signals")
                fig_candles = plot_candlestick_with_signals(
                    results['signals_df'],
                    results['trades'],
                    results['symbol']
                )
                st.plotly_chart(fig_candles, use_container_width=True)
            
            with col2:
                st.subheader("💰 Equity Curve")
                if not results['equity_curve'].empty:
                    fig_equity = plot_equity_curve(results['equity_curve'])
                    st.plotly_chart(fig_equity, use_container_width=True)
            
            # Trade log
            st.markdown("---")
            st.subheader("📋 Trade Log")
            
            trades_display = results['trades'].copy()
            
            # Convert UTC to IST (UTC + 5:30)
            trades_display['entry_date'] = pd.to_datetime(trades_display['entry_date'])
            trades_display['exit_date'] = pd.to_datetime(trades_display['exit_date'])
            
            # Convert pattern_date if it exists
            if 'pattern_date' in trades_display.columns:
                trades_display['pattern_date'] = pd.to_datetime(trades_display['pattern_date'])
                # Add IST offset if timezone aware
                if trades_display['pattern_date'].dt.tz is not None:
                    trades_display['pattern_date'] = trades_display['pattern_date'] + pd.Timedelta(hours=5, minutes=30)
                trades_display['pattern_date'] = trades_display['pattern_date'].dt.strftime('%d-%b-%Y %H:%M IST')
            
            # Add IST offset if timezone aware
            if trades_display['entry_date'].dt.tz is not None:
                trades_display['entry_date'] = trades_display['entry_date'] + pd.Timedelta(hours=5, minutes=30)
                trades_display['exit_date'] = trades_display['exit_date'] + pd.Timedelta(hours=5, minutes=30)
            
            trades_display['entry_date'] = trades_display['entry_date'].dt.strftime('%d-%b-%Y %H:%M IST')
            trades_display['exit_date'] = trades_display['exit_date'].dt.strftime('%d-%b-%Y %H:%M IST')
            
            # Format numeric columns
            trades_display['entry_price'] = trades_display['entry_price'].round(2)
            trades_display['exit_price'] = trades_display['exit_price'].round(2)
            trades_display['pnl'] = trades_display['pnl'].round(2)
            trades_display['pnl_percent'] = trades_display['pnl_percent'].round(2)
            
            # Reorder columns to show pattern_date first
            if 'pattern_date' in trades_display.columns:
                cols = ['symbol', 'position_type', 'pattern_date', 'entry_date', 'exit_date', 
                       'entry_price', 'exit_price', 'quantity', 'stop_loss', 'target', 
                       'exit_reason', 'pnl', 'pnl_percent']
                # Only include columns that exist
                cols = [col for col in cols if col in trades_display.columns]
                trades_display = trades_display[cols]
            
            st.dataframe(trades_display, use_container_width=True)
            
            # Download button
            csv = trades_display.to_csv(index=False)
            st.download_button(
                label="📥 Download Trade Log",
                data=csv,
                file_name=f"{results['symbol']}_trades.csv",
                mime="text/csv"
            )
        else:
            st.info("ℹ️ No trades executed during this period. Try adjusting parameters or selecting a different timeframe.")
            
            # Show pattern detection stats
            st.subheader("🔍 Pattern Detection Statistics")
            signals_df = results['signals_df']
            
            if 'is_hammer' in signals_df.columns:
                hammers = len(signals_df[signals_df['is_hammer'] == True])
                st.write(f"Hammer patterns found: {hammers}")
            
            if 'has_downtrend' in signals_df.columns:
                downtrends = len(signals_df[signals_df['has_downtrend'] == True])
                st.write(f"Strict downtrends found: {downtrends}")
            
            st.write(f"Valid signals (downtrend + hammer + breakout): 0")

if __name__ == "__main__":
    main()
