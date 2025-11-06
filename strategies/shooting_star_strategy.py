"""Shooting Star reversal strategy implementation"""
import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy
from patterns.candlestick import CandlestickPatterns
from config import Config


class ShootingStarStrategy(BaseStrategy):
    """
    Shooting Star Reversal Strategy (SHORT/SELL):
    1. Detect 6 consecutive up candles (each not breaking previous low) - uptrend
    2. Identify shooting star candlestick
    3. Entry when next candle breaks below shooting star low (SHORT)
    4. Stop Loss: Shooting star high
    5. Exit at 1:1.5 risk-reward ratio (minimum)
    """

    def __init__(self, uptrend_candles=6, risk_reward=1.5):
        super().__init__("Shooting Star Reversal")
        self.uptrend_candles = uptrend_candles
        self.risk_reward = risk_reward
        self.pattern_detector = CandlestickPatterns()

    def generate_signals(self, df):
        """Generate trading signals based on shooting star pattern"""
        df = df.copy()

        # Initialize signal columns
        df['signal'] = 0  # 0: no signal, -1: sell/short
        df['entry_price'] = np.nan
        df['stop_loss'] = np.nan
        df['target'] = np.nan
        df['pattern_date'] = pd.Series(dtype='datetime64[ns, UTC]')  # When shooting star formed
        df['is_shooting_star'] = False
        df['has_uptrend'] = False

        # Iterate through data to detect patterns
        for i in range(self.uptrend_candles, len(df) - 1):
            # Check if current candle is shooting star
            is_shooting_star = self.pattern_detector.is_shooting_star(df.iloc[i])
            df.loc[df.index[i], 'is_shooting_star'] = is_shooting_star

            # If shooting star found, check if there was an uptrend BEFORE it
            if is_shooting_star:
                # Try strict mode first
                has_uptrend = self.pattern_detector.detect_uptrend(
                    df, i, self.uptrend_candles, strict=True
                )
                
                # If no strict uptrend found, try relaxed mode
                if not has_uptrend:
                    has_uptrend = self.pattern_detector.detect_uptrend(
                        df, i, self.uptrend_candles, strict=False
                    )
                
                df.loc[df.index[i], 'has_uptrend'] = has_uptrend

                # If uptrend + shooting star, check ONLY the IMMEDIATE next candle for entry
                if has_uptrend:
                    shooting_star_high = df.iloc[i]['High']
                    shooting_star_low = df.iloc[i]['Low']

                    # ONLY check the immediate next candle (i+1)
                    next_candle = df.iloc[i + 1]
                    
                    # Entry conditions (ALL must be true):
                    # 1. Next candle's LOW must break shooting star low
                    # 2. Next candle's OPEN must be at or below shooting star low (gap down or immediate break)
                    breaks_low = next_candle['Low'] < shooting_star_low
                    opens_below = next_candle['Open'] <= shooting_star_low
                    
                    if breaks_low and opens_below:
                        # Generate sell/short signal
                        entry_price = next_candle['Open']
                        stop_loss = shooting_star_high
                        risk = stop_loss - entry_price
                        
                        # Only proceed if risk is reasonable
                        if risk > 0:
                            target = entry_price - (risk * self.risk_reward)

                            df.loc[df.index[i + 1], 'signal'] = -1  # -1 for SHORT
                            df.loc[df.index[i + 1], 'entry_price'] = entry_price
                            df.loc[df.index[i + 1], 'stop_loss'] = stop_loss
                            df.loc[df.index[i + 1], 'target'] = target
                            df.loc[df.index[i + 1], 'pattern_date'] = df.index[i]  # Shooting star formed at index i
                    
                    # If next candle doesn't break low, this shooting star is SKIPPED
                    # The loop will continue and look for the next shooting star

        return df
