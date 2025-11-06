# 🔨 Reversal Pattern Backtester - Multi-Market

A clean, professional backtesting tool for testing Hammer and Shooting Star reversal patterns across Indian Stocks, Forex, and Crypto markets.

## 📊 Strategy

**Strict Downtrend + Hammer Pattern:**

1. Identify 6 consecutive candles where each doesn't break the previous candle's high
2. Next candle should be a HAMMER (small body, long lower wick)
3. Entry when the candle after hammer breaks above hammer high
4. Stop Loss: Hammer low
5. Target: 1:1.5 Risk-Reward ratio (configurable)

## ✨ Features

- ✅ **Multi-Market Support:** Indian Stocks 🇮🇳 | Forex 💱 | Crypto ₿
- ✅ **Two Strategies:** Hammer (LONG) | Shooting Star (SHORT)
- ✅ Test on 60+ popular symbols across all markets
- ✅ Multiple timeframes (5m, 15m, 30m, 1h, 1d, 1wk)
- ✅ Interactive GUI with Streamlit
- ✅ Visual charts with entry/exit markers
- ✅ Detailed performance metrics
- ✅ Downloadable trade logs
- ✅ Equity curve visualization
- ✅ Configurable capital and position sizing

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run GUI (Recommended)

```bash
streamlit run gui/app.py
```

Then open your browser to `http://localhost:8501`

### 3. Run CLI (Optional)

```bash
python main.py
```

## 📱 Using the GUI

1. **Select Stock:** Choose from popular stocks or enter custom symbol
2. **Choose Timeframe:** Select interval (5m to 1wk)
3. **Set Date Range:** Adjust days of history
4. **Configure Capital:** Set initial capital and position size
5. **Tune Strategy:** Adjust downtrend candles and risk-reward ratio
6. **Run Backtest:** Click the button and view results!

## 📈 Markets & Symbols Included

### 🇮🇳 Indian Stocks (25+)
- Indices: NIFTY 50, BANK NIFTY
- Banks: HDFC Bank, ICICI Bank, SBI, Axis Bank, Kotak Bank
- IT: TCS, Infosys, HCL Tech, Wipro
- Others: Reliance, ITC, Maruti, Titan, Asian Paints, Tata Steel, LT

### 💱 Forex (13+)
- Major Pairs: EUR/USD, GBP/USD, USD/JPY, USD/CHF
- Cross Pairs: EUR/GBP, EUR/JPY, GBP/JPY
- Exotic: USD/INR, EUR/INR, GBP/INR
- Commodity: AUD/USD, USD/CAD, NZD/USD

### ₿ Crypto (15+)
- Top Coins: Bitcoin (BTC), Ethereum (ETH), Binance Coin (BNB)
- Altcoins: Cardano (ADA), Solana (SOL), XRP, Polkadot (DOT)
- DeFi: Chainlink (LINK), Avalanche (AVAX), Polygon (MATIC)
- Others: Dogecoin, Litecoin, Bitcoin Cash, Stellar, Cosmos

## ⚠️ Data Limitations (yfinance)

| Timeframe    | Maximum History |
| ------------ | --------------- |
| 5m, 15m, 30m | Last 60 days    |
| 1h           | Last 2 years    |
| 1d, 1wk      | 10+ years       |


**Happy Backtesting! 🚀**
