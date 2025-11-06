"""Candlestick pattern detection"""
import pandas as pd
import numpy as np

class CandlestickPatterns:
    
    @staticmethod
    def is_hammer(row, body_ratio=0.25, wick_ratio=2.5):
        """
        Detect hammer candlestick pattern (STRICT)
        
        Args:
            row: Single row of OHLC data
            body_ratio: Max body size as ratio of total range (stricter: 0.25)
            wick_ratio: Min lower wick to body ratio (stricter: 2.5)
        
        Returns:
            Boolean indicating if it's a hammer
        """
        open_price = row['Open']
        high = row['High']
        low = row['Low']
        close = row['Close']
        
        # Calculate components
        body = abs(close - open_price)
        total_range = high - low
        lower_wick = min(open_price, close) - low
        upper_wick = high - max(open_price, close)
        
        # Avoid division by zero or very small ranges
        if total_range == 0 or total_range < 0.0001:
            return False
        
        # Avoid doji patterns (body too small)
        if body < (total_range * 0.05):  # Body must be at least 5% of range
            return False
        
        # Hammer conditions (STRICTER):
        # 1. Small body (body <= 25% of total range)
        # 2. Long lower wick (lower wick >= 2.5x body)
        # 3. Small upper wick (upper wick <= 0.5x body)
        # 4. Lower wick must be significant (at least 60% of total range)
        is_small_body = (body / total_range) <= body_ratio
        is_long_lower_wick = lower_wick >= (wick_ratio * body)
        is_small_upper_wick = upper_wick <= (body * 0.5)
        is_lower_wick_dominant = (lower_wick / total_range) >= 0.6
        
        return is_small_body and is_long_lower_wick and is_small_upper_wick and is_lower_wick_dominant
    
    @staticmethod
    def detect_downtrend(df, index, num_candles=6, strict=True):
        """
        Detect downtrend with strict or relaxed mode
        
        Args:
            df: DataFrame with OHLC data
            index: Current index position
            num_candles: Number of consecutive down candles required
            strict: If True, each candle must not break previous high. If False, just check bearish candles
        
        Returns:
            Boolean indicating downtrend presence
        """
        if index < num_candles:
            return False
        
        if strict:
            # STRICT MODE: Each candle doesn't break the previous candle's high
            for i in range(1, num_candles + 1):
                current_idx = index - i
                prev_idx = index - i - 1
                
                if prev_idx < 0:
                    return False
                
                current_high = df.iloc[current_idx]['High']
                prev_high = df.iloc[prev_idx]['High']
                
                # Current candle should NOT break previous candle's high
                if current_high >= prev_high:
                    return False
            
            return True
        else:
            # RELAXED MODE: Just check if most candles are bearish
            bearish_count = 0
            for i in range(1, num_candles + 1):
                idx = index - i
                if df.iloc[idx]['Close'] < df.iloc[idx]['Open']:
                    bearish_count += 1
            
            # Require at least 70% bearish candles
            return bearish_count >= (num_candles * 0.7)
    
    @staticmethod
    def is_bullish_engulfing(curr_row, prev_row):
        """Detect bullish engulfing pattern"""
        # Previous candle is bearish
        prev_bearish = prev_row['Close'] < prev_row['Open']
        # Current candle is bullish
        curr_bullish = curr_row['Close'] > curr_row['Open']
        # Current body engulfs previous body
        engulfs = (curr_row['Open'] < prev_row['Close'] and 
                   curr_row['Close'] > prev_row['Open'])
        
        return prev_bearish and curr_bullish and engulfs
    
    @staticmethod
    def is_doji(row, threshold=0.1):
        """Detect doji pattern (open ≈ close)"""
        body = abs(row['Close'] - row['Open'])
        total_range = row['High'] - row['Low']
        
        if total_range == 0:
            return False
        
        return (body / total_range) <= threshold
    
    @staticmethod
    def is_shooting_star(row, body_ratio=0.25, wick_ratio=2.5):
        """
        Detect shooting star candlestick pattern (opposite of hammer)
        
        Args:
            row: Single row of OHLC data
            body_ratio: Max body size as ratio of total range (stricter: 0.25)
            wick_ratio: Min upper wick to body ratio (stricter: 2.5)
        
        Returns:
            Boolean indicating if it's a shooting star
        """
        open_price = row['Open']
        high = row['High']
        low = row['Low']
        close = row['Close']
        
        # Calculate components
        body = abs(close - open_price)
        total_range = high - low
        upper_wick = high - max(open_price, close)
        lower_wick = min(open_price, close) - low
        
        # Avoid division by zero or very small ranges
        if total_range == 0 or total_range < 0.0001:
            return False
        
        # Avoid doji patterns (body too small)
        if body < (total_range * 0.05):  # Body must be at least 5% of range
            return False
        
        # Shooting star conditions (STRICTER):
        # 1. Small body (body <= 25% of total range)
        # 2. Long upper wick (upper wick >= 2.5x body)
        # 3. Small lower wick (lower wick <= 0.5x body, not just <= body)
        # 4. Upper wick must be significant (at least 60% of total range)
        is_small_body = (body / total_range) <= body_ratio
        is_long_upper_wick = upper_wick >= (wick_ratio * body)
        is_small_lower_wick = lower_wick <= (body * 0.5)
        is_upper_wick_dominant = (upper_wick / total_range) >= 0.6
        
        return is_small_body and is_long_upper_wick and is_small_lower_wick and is_upper_wick_dominant
    
    @staticmethod
    def detect_uptrend(df, index, num_candles=6, strict=True):
        """
        Detect uptrend with strict or relaxed mode
        
        Args:
            df: DataFrame with OHLC data
            index: Current index position
            num_candles: Number of consecutive up candles required
            strict: If True, each candle must not break previous low. If False, just check bullish candles
        
        Returns:
            Boolean indicating uptrend presence
        """
        if index < num_candles:
            return False
        
        if strict:
            # STRICT MODE: Each candle doesn't break the previous candle's low
            for i in range(1, num_candles + 1):
                current_idx = index - i
                prev_idx = index - i - 1
                
                if prev_idx < 0:
                    return False
                
                current_low = df.iloc[current_idx]['Low']
                prev_low = df.iloc[prev_idx]['Low']
                
                # Current candle should NOT break previous candle's low
                if current_low <= prev_low:
                    return False
            
            return True
        else:
            # RELAXED MODE: Just check if most candles are bullish
            bullish_count = 0
            for i in range(1, num_candles + 1):
                idx = index - i
                if df.iloc[idx]['Close'] > df.iloc[idx]['Open']:
                    bullish_count += 1
            
            # Require at least 70% bullish candles
            return bullish_count >= (num_candles * 0.7)
