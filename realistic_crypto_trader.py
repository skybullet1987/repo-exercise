"""
RealisticCryptoTrader - A cryptocurrency trading algorithm with realistic backtest/live parity

This module provides backward compatibility by re-exporting all components.
The implementation has been split into modular files for better organization:
- trading_types.py: Enum definitions (ExecutionMode, OrderType, OrderSide)
- models.py: SlippageModel and FeeModel
- validators.py: OrderValidator
- execution_logger.py: ExecutionLogger
- trader.py: RealisticCryptoTrader main class

For new code, consider importing directly from the specific modules.
"""

# Re-export all components for backward compatibility
from trading_types import ExecutionMode, OrderType, OrderSide
from models import SlippageModel, FeeModel
from validators import OrderValidator
from execution_logger import ExecutionLogger
from trader import RealisticCryptoTrader, main

__all__ = [
    'ExecutionMode',
    'OrderType',
    'OrderSide',
    'SlippageModel',
    'FeeModel',
    'OrderValidator',
    'ExecutionLogger',
    'RealisticCryptoTrader',
    'main'
]


if __name__ == "__main__":
    main()
