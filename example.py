#!/usr/bin/env python3
"""
Example script demonstrating RealisticCryptoTrader usage

This script shows how to:
1. Configure the trader with realistic parameters
2. Execute trades in backtest mode
3. Validate orders
4. Compare conservative vs aggressive configurations
5. Review execution statistics
"""

from realistic_crypto_trader import (
    RealisticCryptoTrader,
    ExecutionMode,
    OrderSide,
    OrderType
)


def main():
    print("=" * 70)
    print("RealisticCryptoTrader Example")
    print("=" * 70)
    
    # Configuration for conservative execution (recommended for live trading)
    conservative_config = {
        'log_level': 'INFO',
        'initial_cash': 10000.0,
        'slippage': {
            'base_bps': 10.0,           # 0.1% base slippage
            'volatility_multiplier': 1.5  # Account for volatility
        },
        'fees': {
            'maker_bps': 10.0,           # 0.1% maker fee
            'taker_bps': 20.0            # 0.2% taker fee
        },
        'validator': {
            'min_notional': 10.0,
            'lot_size': 0.00001,
            'price_precision': 2
        },
        'execution_latency_ms': 100,
        'execution_log_file': 'example_backtest_log.json'
    }
    
    print("\n1. Running Backtest Simulation")
    print("-" * 70)
    
    # Initialize trader in backtest mode
    trader = RealisticCryptoTrader(ExecutionMode.BACKTEST, conservative_config)
    
    # Example 1: Buy BTC with market order
    print("\nBuying 0.1 BTC...")
    buy_btc = trader.execute_order(
        symbol='BTC/USD',
        side=OrderSide.BUY,
        quantity=0.1,
        price=50000.0,
        order_type=OrderType.MARKET,
        volume_24h=1000.0,    # BTC 24h volume
        spread_pct=0.05       # 0.05% spread
    )
    
    if buy_btc['success']:
        print(f"  ✓ Filled at ${buy_btc['fill_price']:.2f}")
        print(f"    Expected: ${buy_btc['expected_price']:.2f}")
        print(f"    Slippage: ${buy_btc['slippage']:.2f} ({buy_btc['slippage_bps']:.2f} bps)")
        print(f"    Fee: ${buy_btc['fee']:.2f}")
    else:
        print(f"  ✗ Failed: {buy_btc['error']}")
    
    # Example 2: Buy ETH with market order
    print("\nBuying 1.5 ETH...")
    buy_eth = trader.execute_order(
        symbol='ETH/USD',
        side=OrderSide.BUY,
        quantity=1.5,
        price=3000.0,
        order_type=OrderType.MARKET,
        volume_24h=5000.0,
        spread_pct=0.05
    )
    
    if buy_eth['success']:
        print(f"  ✓ Filled at ${buy_eth['fill_price']:.2f}")
        print(f"    Slippage: ${buy_eth['slippage']:.2f} ({buy_eth['slippage_bps']:.2f} bps)")
        print(f"    Fee: ${buy_eth['fee']:.2f}")
    
    # Example 3: Sell BTC with limit order (maker fee)
    print("\nSelling 0.05 BTC with limit order...")
    sell_btc = trader.execute_order(
        symbol='BTC/USD',
        side=OrderSide.SELL,
        quantity=0.05,
        price=52000.0,
        order_type=OrderType.LIMIT,  # Limit order = maker fee
        volume_24h=1000.0,
        spread_pct=0.05
    )
    
    if sell_btc['success']:
        print(f"  ✓ Filled at ${sell_btc['fill_price']:.2f}")
        print(f"    Slippage: ${sell_btc['slippage']:.2f} ({sell_btc['slippage_bps']:.2f} bps)")
        print(f"    Fee: ${sell_btc['fee']:.2f} (maker: {sell_btc['is_maker']})")
    
    # Show portfolio
    print("\n2. Portfolio Status")
    print("-" * 70)
    portfolio = trader.get_portfolio()
    print(f"Cash: ${portfolio['cash']:.2f}")
    for symbol, quantity in portfolio['positions'].items():
        print(f"{symbol}: {quantity}")
    
    # Show execution statistics
    print("\n3. Execution Statistics")
    print("-" * 70)
    stats = trader.get_execution_stats()
    print(f"Total orders executed: {stats['total_orders']}")
    print(f"Total slippage: ${stats['total_slippage']:.2f}")
    print(f"Average slippage: ${stats['avg_slippage']:.2f}")
    print(f"Total fees: ${stats['total_fees']:.2f}")
    print(f"Average fees: ${stats['avg_fees']:.2f}")
    
    # Test order validation
    print("\n4. Order Validation Examples")
    print("-" * 70)
    
    # Order below minimum notional
    print("\nTrying order below minimum notional...")
    small_order = trader.execute_order(
        symbol='BTC/USD',
        side=OrderSide.BUY,
        quantity=0.0001,
        price=50.0  # Notional = $0.005, below $10 minimum
    )
    print(f"  Result: {'✓ Rejected' if not small_order['success'] else '✗ Accepted'}")
    if not small_order['success']:
        print(f"  Reason: {small_order['error']}")
    
    # Order with insufficient balance
    print("\nTrying order with insufficient cash...")
    large_order = trader.execute_order(
        symbol='BTC/USD',
        side=OrderSide.BUY,
        quantity=10.0,
        price=50000.0  # Would cost ~$500,000
    )
    print(f"  Result: {'✓ Rejected' if not large_order['success'] else '✗ Accepted'}")
    if not large_order['success']:
        print(f"  Reason: {large_order['error']}")
    
    # Finalize and save
    print("\n5. Saving Results")
    print("-" * 70)
    trader.finalize()
    print("  ✓ Execution log saved to example_backtest_log.json")
    print("  ✓ Portfolio state saved to portfolio_state.json")
    
    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Review example_backtest_log.json for detailed execution data")
    print("  2. Adjust configuration parameters for your use case")
    print("  3. Run backtests with historical data")
    print("  4. Compare backtest vs live performance")
    print("\nSee SOLUTION.md for detailed documentation.")


if __name__ == "__main__":
    main()
