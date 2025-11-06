"""Configuration settings for the backtester"""

class Config:
    # Data settings
    DATA_CACHE_DIR = "cache"
    DEFAULT_MARKET = "NSE"  # NSE or BSE
    
    # Backtesting settings
    INITIAL_CAPITAL = 500000  # Starting capital in INR (5 lakhs for index trading)
    COMMISSION = 0.0003  # 0.03% per trade
    SLIPPAGE = 0.0001  # 0.01% slippage
    
    # Risk management
    MAX_POSITION_SIZE = 0.1  # Max 10% of capital per trade
    DEFAULT_RISK_REWARD = 1.5  # 1:1.5 risk-reward ratio
    
    # Pattern detection thresholds
    HAMMER_BODY_RATIO = 0.3  # Body should be <= 30% of total range
    HAMMER_WICK_RATIO = 2.0  # Lower wick should be >= 2x body
    DOWNTREND_CANDLES = 6  # Number of down candles for trend
