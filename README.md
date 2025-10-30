# repo-exercise

## RealisticCryptoTrader - Bridging the Gap Between Backtest and Live Trading

This repository contains a comprehensive solution to the common problem of algorithms that perform well in backtesting but poorly in live trading.

### Problem

Many trading algorithms show excellent simulated returns but fail in live markets due to:
- Unrealistic slippage and fee models
- Lack of order validation
- Missing latency simulation
- State synchronization issues
- Differences in execution logic between backtest and live modes

### Solution

`RealisticCryptoTrader` implements a unified trading framework with:

✅ **Realistic Slippage Modeling** - Market impact, spread, and volatility-adjusted slippage
✅ **Comprehensive Fee Handling** - Maker/taker fees with exchange-specific tiers
✅ **Order Validation** - Minimum notional and lot size enforcement
✅ **Execution Latency** - Simulated delays matching real-world conditions
✅ **Detailed Logging** - Track and compare backtest vs live execution quality
✅ **State Persistence** - Portfolio synchronization across sessions

### Quick Start

```python
from realistic_crypto_trader import RealisticCryptoTrader, ExecutionMode, OrderSide

# Configure with realistic parameters
config = {
    'initial_cash': 10000.0,
    'slippage': {'base_bps': 5.0, 'volatility_multiplier': 1.5},
    'fees': {'maker_bps': 10.0, 'taker_bps': 20.0}
}

# Initialize trader
trader = RealisticCryptoTrader(ExecutionMode.BACKTEST, config)

# Execute trade
result = trader.execute_order(
    symbol='BTC/USD',
    side=OrderSide.BUY,
    quantity=0.1,
    price=50000.0
)

# Review statistics
stats = trader.get_execution_stats()
print(f"Slippage: {stats['avg_slippage']}, Fees: {stats['avg_fees']}")
```

### Running Tests

```bash
python -m unittest test_realistic_crypto_trader -v
```

All 24 tests should pass, validating:
- Slippage calculations
- Fee models
- Order validation
- Execution logic
- Portfolio management
- State persistence

### Documentation

See [SOLUTION.md](SOLUTION.md) for:
- Detailed architecture explanation
- Configuration options
- Usage examples
- Best practices
- Troubleshooting guide

### Key Features

| Feature | Backtest | Live | Benefit |
|---------|----------|------|---------|
| Slippage Model | ✅ | ✅ | Consistent cost modeling |
| Fee Calculation | ✅ | ✅ | Accurate P&L |
| Order Validation | ✅ | ✅ | Same rejection rules |
| Latency Simulation | ✅ | Natural | Realistic timing |
| Execution Logging | ✅ | ✅ | Performance comparison |

### Files

- `realistic_crypto_trader.py` - Main implementation
- `test_realistic_crypto_trader.py` - Comprehensive test suite
- `SOLUTION.md` - Detailed documentation
- `README.md` - This file

### Example Output

```
=== BACKTEST MODE ===
Order executed successfully: filled @ 50431.25, slippage=43.1250, fee=10.0862
Portfolio: {'cash': 7481.82, 'positions': {'BTC/USD': 0.05}}
Statistics: {'total_orders': 2, 'total_slippage': 55.56, 'avg_slippage': 27.78, 
            'total_fees': 12.62, 'avg_fees': 6.31}
```

### Contributing

This implementation addresses the core issue described in the repository. Future enhancements could include:
- Integration with live exchange APIs
- Additional order types (stop-loss, take-profit)
- Portfolio optimization algorithms
- Risk management features
- Performance attribution analysis

### License

This is an exercise repository for demonstrating solutions to real-world trading algorithm issues.