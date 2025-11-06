"""Core backtesting engine"""
import pandas as pd
import numpy as np
from backtester.portfolio import Portfolio
from config import Config

class BacktestEngine:
    """Main backtesting engine"""
    
    def __init__(self, strategy, initial_capital=None, commission=None, slippage=None):
        self.strategy = strategy
        self.initial_capital = initial_capital or Config.INITIAL_CAPITAL
        self.commission = commission or Config.COMMISSION
        self.slippage = slippage or Config.SLIPPAGE
        self.portfolio = None
        self.results = None
    
    def run(self, df, symbol="STOCK"):
        """
        Run backtest on data
        
        Args:
            df: DataFrame with OHLC data
            symbol: Stock symbol
        
        Returns:
            Dictionary with backtest results
        """
        # Generate signals
        print(f"Generating signals for {symbol}...")
        df_signals = self.strategy.generate_signals(df)
        
        # Initialize portfolio
        self.portfolio = Portfolio(
            self.initial_capital,
            self.commission,
            self.slippage
        )
        
        # Execute trades
        print(f"Executing trades...")
        for i in range(len(df_signals)):
            row = df_signals.iloc[i]
            date = df_signals.index[i]
            
            # Check for exit conditions FIRST (before new entries)
            if self.portfolio.current_position:
                pos = self.portfolio.current_position
                current_high = row['High']
                current_low = row['Low']
                
                # Don't exit on the same candle we entered
                if pos.entry_date != date:
                    if pos.position_type == 'LONG':
                        # LONG position exits
                        if current_low <= pos.stop_loss:
                            self.portfolio.close_position(date, pos.stop_loss, "Stop Loss")
                        elif current_high >= pos.target:
                            self.portfolio.close_position(date, pos.target, "Target")
                    
                    elif pos.position_type == 'SHORT':
                        # SHORT position exits (opposite logic)
                        if current_high >= pos.stop_loss:
                            self.portfolio.close_position(date, pos.stop_loss, "Stop Loss")
                        elif current_low <= pos.target:
                            self.portfolio.close_position(date, pos.target, "Target")
            
            # Check for entry signal (LONG or SHORT) - only if no position open
            if row['signal'] != 0 and self.portfolio.current_position is None:
                position_type = 'LONG' if row['signal'] == 1 else 'SHORT'
                success = self.portfolio.open_position(
                    date,
                    row['entry_price'],
                    row['stop_loss'],
                    row['target'],
                    symbol,
                    Config.MAX_POSITION_SIZE,
                    position_type
                )
                # Store pattern date if position opened successfully
                if success and self.portfolio.current_position and 'pattern_date' in row and pd.notna(row['pattern_date']):
                    self.portfolio.current_position.pattern_date = row['pattern_date']
            
            # Update equity curve
            current_price = row['Close']
            self.portfolio.update_equity(date, current_price)
        
        # Close any remaining open position
        if self.portfolio.current_position:
            last_row = df_signals.iloc[-1]
            self.portfolio.close_position(
                df_signals.index[-1],
                last_row['Close'],
                "End of Data"
            )
        
        # Compile results
        self.results = self._compile_results(df_signals, symbol)
        
        return self.results
    
    def _compile_results(self, df_signals, symbol):
        """Compile backtest results"""
        trades_df = self.portfolio.get_trades_df()
        equity_df = self.portfolio.get_equity_df()
        
        if trades_df.empty:
            return {
                'symbol': symbol,
                'strategy': self.strategy.name,
                'initial_capital': self.initial_capital,
                'final_capital': self.portfolio.cash,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_return': 0,
                'max_drawdown': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'trades': trades_df,
                'equity_curve': equity_df,
                'signals_df': df_signals
            }
        
        # Calculate metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = trades_df['pnl'].sum()
        total_return = ((self.portfolio.cash - self.initial_capital) / self.initial_capital) * 100
        
        # Calculate max drawdown
        equity_df['peak'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100
        max_drawdown = equity_df['drawdown'].min()
        
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        
        return {
            'symbol': symbol,
            'strategy': self.strategy.name,
            'initial_capital': self.initial_capital,
            'final_capital': self.portfolio.cash,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            'trades': trades_df,
            'equity_curve': equity_df,
            'signals_df': df_signals
        }
