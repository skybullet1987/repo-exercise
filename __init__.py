"""
RealisticCryptoTrader Package

A modular cryptocurrency trading algorithm with realistic backtest/live parity.

Modules:
- trading_types: Enum definitions
- models: Slippage and Fee models
- validators: Order validator
- execution_logger: Execution logger
- trader: Main RealisticCryptoTrader class

For backward compatibility, all components can be imported from the main module:
    from realistic_crypto_trader import RealisticCryptoTrader, ExecutionMode, OrderSide
"""

__version__ = '1.0.0'
__author__ = 'RealisticCryptoTrader Team'

from realistic_crypto_trader import (
    ExecutionMode,
    OrderType,
    OrderSide,
    SlippageModel,
    FeeModel,
    OrderValidator,
    ExecutionLogger,
    RealisticCryptoTrader,
    main
)

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
