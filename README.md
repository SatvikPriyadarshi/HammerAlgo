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

## 📁 Project Structure

```
trading-backtester/
├── data/
│   └── data_fetcher.py      # Fetch data from yfinance
├── strategies/
│   ├── base_strategy.py     # Base strategy class
│   └── hammer_strategy.py   # Hammer pattern strategy
├── backtester/
│   ├── engine.py            # Backtesting engine
│   └── portfolio.py         # Position management
├── patterns/
│   └── candlestick.py       # Pattern detection
├── gui/
│   └── app.py               # Streamlit GUI
├── config.py                # Configuration
├── main.py                  # CLI entry point
└── requirements.txt
```

## 🎯 Strategy Performance

The strict downtrend rule makes this a **high-quality, low-frequency** strategy:

- Very selective (few signals)
- Higher win rate when signals occur
- Suitable for swing trading
- Works best on daily/hourly timeframes

## 💡 Tips for Best Results

1. **For Intraday:** Use 15m or 1h timeframe (limited history)
2. **For Swing Trading:** Use 1d timeframe (years of data)
3. **Capital:** Start with Rs.1 lakh for stocks, Rs.5 lakhs for indices
4. **Position Size:** Risk 1-2% per trade (10% of capital)
5. **Testing:** Always backtest before live trading

## 🔧 Configuration

Edit `config.py` to change:

- Initial capital
- Commission rates
- Slippage
- Position sizing
- Pattern detection thresholds

## 📝 Adding New Strategies

1. Create new file in `strategies/` folder
2. Inherit from `BaseStrategy` class
3. Implement `generate_signals()` method
4. Return DataFrame with: `signal`, `entry_price`, `stop_loss`, `target`

## ⚖️ Disclaimer

This is a backtesting tool for educational purposes. Past performance does not guarantee future results. Always:

- Paper trade first
- Use proper risk management
- Never risk more than you can afford to lose
- Consult a financial advisor before trading

## 📄 License

MIT License - Feel free to use and modify!

---

**Happy Backtesting! 🚀**
