"""
Type definitions and enums for RealisticCryptoTrader
"""

from enum import Enum


class ExecutionMode(Enum):
    """Trading execution mode"""
    BACKTEST = "backtest"
    LIVE = "live"


class OrderType(Enum):
    """Order types supported"""
    MARKET = "market"
    LIMIT = "limit"


class OrderSide(Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"
