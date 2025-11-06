"""Main entry point for the backtester"""
import sys
from datetime import datetime, timedelta
from data.data_fetcher import DataFetcher
from strategies.hammer_strategy import HammerStrategy
from backtester.engine import BacktestEngine
from config import Config


def run_cli_backtest():
    """Run backtest from command line"""
    print("=" * 80)
    print("HAMMER PATTERN BACKTESTER - Strict Downtrend Strategy")
    print("=" * 80)

    # Configuration
    symbol = "HDFCBANK"
    market = "NSE"
    interval = "1d"
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    print(f"\nSymbol: {symbol}")
    print(f"Market: {market}")
    print(f"Timeframe: {interval}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Initial Capital: Rs.{Config.INITIAL_CAPITAL:,.0f}")
    
    print("\nStrategy: 6 consecutive candles (each not breaking previous high) + Hammer")
    print("=" * 80)

    # Fetch data
    print("\nFetching data...")
    fetcher = DataFetcher()
    df = fetcher.fetch_stock_data(symbol, start_date, end_date, interval=interval, market=market)

    if df.empty:
        print(f"Error: No data found for {symbol}")
        return

    print(f"Loaded {len(df)} candles")

    # Run backtest
    print("\nRunning backtest...")
    strategy = HammerStrategy(downtrend_candles=6, risk_reward=1.5)
    engine = BacktestEngine(strategy)
    results = engine.run(df, symbol)

    # Display results
    print("\n" + "=" * 80)
    print("BACKTEST RESULTS")
    print("=" * 80)
    print(f"Strategy: {results['strategy']}")
    print(f"Symbol: {results['symbol']}")
    print(f"\nCapital:")
    print(f"  Initial: Rs.{results['initial_capital']:,.2f}")
    print(f"  Final: Rs.{results['final_capital']:,.2f}")
    print(f"\nPerformance:")
    print(f"  Total Return: {results['total_return']:.2f}%")
    print(f"  Total P&L: Rs.{results['total_pnl']:,.2f}")
    print(f"  Max Drawdown: {results['max_drawdown']:.2f}%")
    print(f"\nTrades:")
    print(f"  Total: {results['total_trades']}")
    print(f"  Winning: {results['winning_trades']}")
    print(f"  Losing: {results['losing_trades']}")
    print(f"  Win Rate: {results['win_rate']:.2f}%")
    
    if results['total_trades'] > 0:
        print(f"\nRisk Metrics:")
        print(f"  Avg Win: Rs.{results['avg_win']:.2f}")
        print(f"  Avg Loss: Rs.{results['avg_loss']:.2f}")
        print(f"  Profit Factor: {results['profit_factor']:.2f}")
    
    print("=" * 80)

    # Show trade log
    if not results["trades"].empty:
        print("\nTrade Log:")
        print(results["trades"].to_string())
    else:
        print("\nNo trades executed. Try different parameters or longer time period.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "gui":
        print("Starting GUI mode...")
        print("Run: streamlit run gui/app.py")
    else:
        run_cli_backtest()


if __name__ == "__main__":
    main()
