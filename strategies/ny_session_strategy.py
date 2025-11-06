"""New York Session Range Breakout Strategy"""
import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy
from datetime import time
import pytz


class NYSessionStrategy(BaseStrategy):
    """
    New York Session Range Breakout Strategy:
    1. Identify first 4-hour candle of NY session (8:00 AM - 12:00 PM EST)
    2. Mark the high and low of this 4-hour range
    3. On 5-min timeframe, wait for breakout with body (close outside range)
    4. When candle closes ENTIRELY back inside range, enter trade
    5. Entry: High (for SHORT) or Low (for LONG) of re-entry candle
    6. Stop Loss: Extreme of all breakout candles
    7. Target: Minimum 1:8 risk-reward
    """

    def __init__(self, session_start_hour=8, session_start_minute=0, risk_reward=8.0):
        super().__init__("NY Session Range Breakout")
        self.session_start_hour = session_start_hour  # 8 AM EST for Forex/Gold
        self.session_start_minute = session_start_minute
        self.risk_reward = risk_reward
        self.ny_tz = pytz.timezone('America/New_York')

    def generate_signals(self, df):
        """Generate trading signals based on NY session range breakout"""
        df = df.copy()

        # Initialize signal columns
        df['signal'] = 0  # 0: no signal, 1: long, -1: short
        df['entry_price'] = np.nan
        df['stop_loss'] = np.nan
        df['target'] = np.nan
        df['pattern_date'] = pd.Series(dtype='datetime64[ns, UTC]')
        df['four_hour_high'] = np.nan
        df['four_hour_low'] = np.nan

        # Ensure index is datetime with timezone
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        
        # Convert to NY timezone for session identification
        df_ny = df.copy()
        df_ny.index = df_ny.index.tz_convert(self.ny_tz)

        # Group by date to process each day
        for date, day_data in df_ny.groupby(df_ny.index.date):
            # Find the 4-hour range (first 4 hours of NY session)
            session_start = pd.Timestamp(date).replace(
                hour=self.session_start_hour,
                minute=self.session_start_minute,
                second=0
            )
            session_start = self.ny_tz.localize(session_start)
            session_end = session_start + pd.Timedelta(hours=4)

            # Get candles in the 4-hour window
            four_hour_candles = day_data[
                (day_data.index >= session_start) & 
                (day_data.index < session_end)
            ]

            if len(four_hour_candles) == 0:
                continue

            # Calculate 4-hour range
            four_hour_high = four_hour_candles['High'].max()
            four_hour_low = four_hour_candles['Low'].min()

            # Get candles after the 4-hour window
            after_session = day_data[day_data.index >= session_end]

            if len(after_session) == 0:
                continue

            # Store 4-hour range in dataframe
            after_indices = after_session.index
            for idx in after_indices:
                # Convert back to UTC for storage
                utc_idx = idx.tz_convert('UTC')
                if utc_idx in df.index:
                    df.loc[utc_idx, 'four_hour_high'] = four_hour_high
                    df.loc[utc_idx, 'four_hour_low'] = four_hour_low

            # Track breakout state
            in_breakout_up = False
            in_breakout_down = False
            breakout_high = None
            breakout_low = None

            # Process candles after 4-hour session
            for i in range(len(after_session)):
                candle = after_session.iloc[i]
                candle_idx_ny = after_session.index[i]
                candle_idx_utc = candle_idx_ny.tz_convert('UTC')

                if candle_idx_utc not in df.index:
                    continue

                # Check for breakout ABOVE (with body)
                if candle['Close'] > four_hour_high and not in_breakout_up and not in_breakout_down:
                    in_breakout_up = True
                    breakout_high = candle['High']  # Start tracking HIGHEST high for stop loss
                    breakout_low = candle['Low']  # Also track lowest low

                # Check for breakout BELOW (with body)
                elif candle['Close'] < four_hour_low and not in_breakout_down and not in_breakout_up:
                    in_breakout_down = True
                    breakout_low = candle['Low']  # Start tracking LOWEST low for stop loss
                    breakout_high = candle['High']  # Also track highest high

                # If in upward breakout, track extremes
                if in_breakout_up:
                    if candle['High'] > breakout_high:
                        breakout_high = candle['High']
                    if candle['Low'] < breakout_low:
                        breakout_low = candle['Low']

                    # Check if ENTIRE candle is back inside range
                    if (candle['High'] <= four_hour_high and 
                        candle['Low'] >= four_hour_low and
                        candle['Open'] <= four_hour_high and 
                        candle['Open'] >= four_hour_low and
                        candle['Close'] <= four_hour_high and 
                        candle['Close'] >= four_hour_low):
                        
                        # Enter SHORT
                        entry_price = candle['High']
                        stop_loss = breakout_high  # Stop at HIGHEST point of breakout
                        risk = stop_loss - entry_price  # For SHORT: SL is above entry

                        if risk > 0:
                            target = entry_price - (risk * self.risk_reward)

                            df.loc[candle_idx_utc, 'signal'] = -1
                            df.loc[candle_idx_utc, 'entry_price'] = entry_price
                            df.loc[candle_idx_utc, 'stop_loss'] = stop_loss
                            df.loc[candle_idx_utc, 'target'] = target
                            df.loc[candle_idx_utc, 'pattern_date'] = session_start.tz_convert('UTC')

                        # Reset breakout state
                        in_breakout_up = False
                        breakout_high = None
                        breakout_low = None

                # If in downward breakout, track extremes
                if in_breakout_down:
                    if candle['Low'] < breakout_low:
                        breakout_low = candle['Low']
                    if candle['High'] > breakout_high:
                        breakout_high = candle['High']

                    # Check if ENTIRE candle is back inside range
                    if (candle['High'] <= four_hour_high and 
                        candle['Low'] >= four_hour_low and
                        candle['Open'] <= four_hour_high and 
                        candle['Open'] >= four_hour_low and
                        candle['Close'] <= four_hour_high and 
                        candle['Close'] >= four_hour_low):
                        
                        # Enter LONG
                        entry_price = candle['Low']
                        stop_loss = breakout_low  # Stop at LOWEST point of breakout
                        risk = entry_price - stop_loss  # For LONG: SL is below entry

                        if risk > 0:
                            target = entry_price + (risk * self.risk_reward)

                            df.loc[candle_idx_utc, 'signal'] = 1
                            df.loc[candle_idx_utc, 'entry_price'] = entry_price
                            df.loc[candle_idx_utc, 'stop_loss'] = stop_loss
                            df.loc[candle_idx_utc, 'target'] = target
                            df.loc[candle_idx_utc, 'pattern_date'] = session_start.tz_convert('UTC')

                        # Reset breakout state
                        in_breakout_down = False
                        breakout_high = None
                        breakout_low = None

        return df
