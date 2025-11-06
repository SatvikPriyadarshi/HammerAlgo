"""Portfolio and position management"""
import pandas as pd
from datetime import datetime

class Position:
    """Represents a single trading position"""
    
    def __init__(self, entry_date, entry_price, quantity, stop_loss, target, symbol, position_type='LONG'):
        self.entry_date = entry_date
        self.entry_price = entry_price
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.target = target
        self.symbol = symbol
        self.position_type = position_type  # 'LONG' or 'SHORT'
        self.exit_date = None
        self.exit_price = None
        self.exit_reason = None
        self.pnl = 0
        self.pnl_percent = 0
    
    def close(self, exit_date, exit_price, reason):
        """Close the position"""
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_reason = reason
        
        # Calculate P&L based on position type
        if self.position_type == 'LONG':
            self.pnl = (exit_price - self.entry_price) * self.quantity
            self.pnl_percent = ((exit_price - self.entry_price) / self.entry_price) * 100
        else:  # SHORT
            self.pnl = (self.entry_price - exit_price) * self.quantity
            self.pnl_percent = ((self.entry_price - exit_price) / self.entry_price) * 100
    
    def to_dict(self):
        """Convert position to dictionary"""
        return {
            'symbol': self.symbol,
            'position_type': self.position_type,
            'pattern_date': getattr(self, 'pattern_date', None),  # When pattern formed
            'entry_date': self.entry_date,
            'entry_price': self.entry_price,
            'exit_date': self.exit_date,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'stop_loss': self.stop_loss,
            'target': self.target,
            'exit_reason': self.exit_reason,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent
        }

class Portfolio:
    """Manages portfolio and tracks performance"""
    
    def __init__(self, initial_capital, commission=0.0003, slippage=0.0001):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.positions = []
        self.current_position = None
        self.equity_curve = []
    
    def open_position(self, date, entry_price, stop_loss, target, symbol, position_size=0.1, position_type='LONG'):
        """Open a new position (LONG or SHORT)"""
        if self.current_position is not None:
            return False  # Already have an open position
        
        # Calculate position size based on risk
        if position_type == 'LONG':
            risk_per_share = entry_price - stop_loss
        else:  # SHORT
            risk_per_share = stop_loss - entry_price
        
        if risk_per_share <= 0:
            return False
        
        # Method 1: Calculate quantity based on risk
        risk_per_trade = self.cash * position_size
        quantity_by_risk = int(risk_per_trade / risk_per_share)
        
        # Method 2: Calculate max quantity we can afford
        available_cash = self.cash * 0.98  # Keep 2% buffer for commission
        max_quantity = int(available_cash / (entry_price * (1 + self.slippage)))
        
        # Use the smaller of the two
        quantity = min(quantity_by_risk, max_quantity)
        
        if quantity <= 0:
            return False
        
        # Apply slippage and commission
        actual_entry = entry_price * (1 + self.slippage)
        cost = quantity * actual_entry
        commission_cost = cost * self.commission
        total_cost = cost + commission_cost
        
        if total_cost > self.cash:
            return False
        
        # Create position
        self.current_position = Position(date, actual_entry, quantity, stop_loss, target, symbol, position_type)
        self.cash -= total_cost
        
        return True
    
    def close_position(self, date, exit_price, reason):
        """Close the open position"""
        if self.current_position is None:
            return False
        
        # Apply slippage and commission
        actual_exit = exit_price * (1 - self.slippage)
        proceeds = self.current_position.quantity * actual_exit
        commission_cost = proceeds * self.commission
        net_proceeds = proceeds - commission_cost
        
        # Close position
        self.current_position.close(date, actual_exit, reason)
        self.cash += net_proceeds
        self.positions.append(self.current_position)
        self.current_position = None
        
        return True
    
    def update_equity(self, date, current_price=None):
        """Update equity curve"""
        equity = self.cash
        if self.current_position and current_price:
            equity += self.current_position.quantity * current_price
        
        self.equity_curve.append({
            'date': date,
            'equity': equity,
            'cash': self.cash
        })
    
    def get_total_equity(self, current_price=None):
        """Get current total equity"""
        equity = self.cash
        if self.current_position and current_price:
            equity += self.current_position.quantity * current_price
        return equity
    
    def get_trades_df(self):
        """Get all trades as DataFrame"""
        if not self.positions:
            return pd.DataFrame()
        return pd.DataFrame([pos.to_dict() for pos in self.positions])
    
    def get_equity_df(self):
        """Get equity curve as DataFrame"""
        if not self.equity_curve:
            return pd.DataFrame()
        return pd.DataFrame(self.equity_curve)
