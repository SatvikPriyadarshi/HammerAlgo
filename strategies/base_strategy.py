"""Base strategy class for all trading strategies"""
from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name):
        self.name = name
        self.signals = []
    
    @abstractmethod
    def generate_signals(self, df):
        """
        Generate trading signals from data
        
        Args:
            df: DataFrame with OHLC data
        
        Returns:
            DataFrame with additional columns: 'signal', 'entry_price', 'stop_loss', 'target'
        """
        pass
    
    def get_strategy_info(self):
        """Return strategy description"""
        return {
            'name': self.name,
            'description': self.__doc__
        }
