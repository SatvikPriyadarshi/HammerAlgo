"""Hammer reversal strategy implementation"""
import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy
from patterns.candlestick import CandlestickPatterns
from config import Config

class HammerStrategy(BaseStrategy):
    """
    Hammer Reversal Strategy:
    1. Detect 6-7 consecutive down candles (downtrend)
    2. Identify hammer candlestick
    3. Entry when next candle breaks hammer high
    4. Exit at 1:1.5 risk-reward ratio
    """
    
    def __init__(self, downtrend_candles=6, risk_reward=1.5):
        super().__init__("Hammer Reversal")
        self.downtrend_candles = downtrend_candles
        self.risk_reward = risk_reward
        self.pattern_detector = CandlestickPatterns()
    
    def generate_signals(self, df):
        """Generate trading signals based on hammer pattern"""
        df = df.copy()
        
        # Initialize signal columns
        df['signal'] = 0  # 0: no signal, 1: buy
        df['entry_price'] = np.nan
        df['stop_loss'] = np.nan
        df['target'] = np.nan
        df['pattern_date'] = pd.Series(dtype='datetime64[ns, UTC]')  # When hammer formed
        df['is_hammer'] = False
        df['has_downtrend'] = False
        
        # Iterate through data to detect patterns
        for i in range(self.downtrend_candles, len(df) - 1):
            # Check if current candle is hammer
            is_hammer = self.pattern_detector.is_hammer(df.iloc[i])
            df.loc[df.index[i], 'is_hammer'] = is_hammer
            
            # If hammer found, check if there was a downtrend BEFORE it
            if is_hammer:
                # Try strict mode first
                has_downtrend = self.pattern_detector.detect_downtrend(
                    df, i, self.downtrend_candles, strict=True
                )
                
                # If no strict downtrend found, try relaxed mode
                if not has_downtrend:
                    has_downtrend = self.pattern_detector.detect_downtrend(
                        df, i, self.downtrend_candles, strict=False
                    )
                
                df.loc[df.index[i], 'has_downtrend'] = has_downtrend
                
                # If downtrend + hammer, check ONLY the IMMEDIATE next candle for entry
                if has_downtrend:
                    hammer_high = df.iloc[i]['High']
                    hammer_low = df.iloc[i]['Low']
                    
                    # ONLY check the immediate next candle (i+1)
                    next_candle = df.iloc[i + 1]
                    
                    # Entry conditions (ALL must be true):
                    # 1. Next candle's HIGH must break hammer high
                    # 2. Next candle's OPEN must be at or above hammer high (gap up or immediate break)
                    breaks_high = next_candle['High'] > hammer_high
                    opens_above = next_candle['Open'] >= hammer_high
                    
                    if breaks_high and opens_above:
                        # Generate buy signal
                        entry_price = next_candle['Open']
                        stop_loss = hammer_low
                        risk = entry_price - stop_loss
                        
                        # Only proceed if risk is reasonable
                        if risk > 0:
                            target = entry_price + (risk * self.risk_reward)
                            
                            df.loc[df.index[i + 1], 'signal'] = 1
                            df.loc[df.index[i + 1], 'entry_price'] = entry_price
                            df.loc[df.index[i + 1], 'stop_loss'] = stop_loss
                            df.loc[df.index[i + 1], 'target'] = target
                            df.loc[df.index[i + 1], 'pattern_date'] = df.index[i]  # Hammer formed at index i
                    
                    # If next candle doesn't break high, this hammer is SKIPPED
                    # The loop will continue and look for the next hammer
        
        return df
