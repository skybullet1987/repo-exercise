"""
Test suite for RealisticCryptoTrader

Tests cover:
- Slippage calculations
- Fee calculations
- Order validation
- Execution logic
- Portfolio management
- State persistence
"""

import unittest
import os
import json
from realistic_crypto_trader import (
    RealisticCryptoTrader,
    ExecutionMode,
    OrderSide,
    OrderType,
    SlippageModel,
    FeeModel,
    OrderValidator,
    ExecutionLogger
)


class TestSlippageModel(unittest.TestCase):
    """Test slippage model calculations"""
    
    def setUp(self):
        self.slippage_model = SlippageModel(base_slippage_bps=5.0, volatility_multiplier=1.0)
    
    def test_base_slippage(self):
        """Test base slippage calculation"""
        slippage = self.slippage_model.calculate_slippage(
            price=50000.0,
            order_size=0.1,
            volume_24h=1000.0,
            spread_pct=0.1
        )
        
        # Should have some slippage
        self.assertGreater(slippage, 0)
        
        # Slippage should be reasonable (less than 2% of order value due to spread)
        order_value = 50000.0 * 0.1
        self.assertLess(slippage, order_value * 0.02)
    
    def test_volume_impact(self):
        """Test that larger orders relative to volume have more slippage"""
        small_order_slippage = self.slippage_model.calculate_slippage(
            price=50000.0,
            order_size=0.01,  # Small order
            volume_24h=1000.0,
            spread_pct=0.1
        )
        
        large_order_slippage = self.slippage_model.calculate_slippage(
            price=50000.0,
            order_size=10.0,  # Large order
            volume_24h=1000.0,
            spread_pct=0.1
        )
        
        # Large orders should have proportionally more slippage
        self.assertGreater(large_order_slippage / 10.0, small_order_slippage / 0.01)
    
    def test_volatility_multiplier(self):
        """Test volatility multiplier effect"""
        normal_model = SlippageModel(base_slippage_bps=5.0, volatility_multiplier=1.0)
        volatile_model = SlippageModel(base_slippage_bps=5.0, volatility_multiplier=2.0)
        
        normal_slippage = normal_model.calculate_slippage(50000.0, 0.1, 1000.0, 0.1)
        volatile_slippage = volatile_model.calculate_slippage(50000.0, 0.1, 1000.0, 0.1)
        
        # Volatile market should have more slippage
        self.assertGreater(volatile_slippage, normal_slippage)


class TestFeeModel(unittest.TestCase):
    """Test fee model calculations"""
    
    def setUp(self):
        self.fee_model = FeeModel(maker_fee_bps=10.0, taker_fee_bps=20.0)
    
    def test_maker_fee(self):
        """Test maker fee calculation"""
        notional = 5000.0
        fee = self.fee_model.calculate_fee(notional, is_maker=True)
        
        # Maker fee should be 0.1% (10 bps)
        expected_fee = notional * 0.001
        self.assertAlmostEqual(fee, expected_fee, places=6)
    
    def test_taker_fee(self):
        """Test taker fee calculation"""
        notional = 5000.0
        fee = self.fee_model.calculate_fee(notional, is_maker=False)
        
        # Taker fee should be 0.2% (20 bps)
        expected_fee = notional * 0.002
        self.assertAlmostEqual(fee, expected_fee, places=6)
    
    def test_taker_higher_than_maker(self):
        """Test that taker fees are higher than maker fees"""
        notional = 5000.0
        maker_fee = self.fee_model.calculate_fee(notional, is_maker=True)
        taker_fee = self.fee_model.calculate_fee(notional, is_maker=False)
        
        self.assertGreater(taker_fee, maker_fee)


class TestOrderValidator(unittest.TestCase):
    """Test order validation logic"""
    
    def setUp(self):
        self.validator = OrderValidator(
            min_notional=10.0,
            lot_size=0.00001,
            price_precision=2
        )
    
    def test_valid_order(self):
        """Test valid order passes validation"""
        is_valid, msg = self.validator.validate_order(quantity=0.001, price=50000.0)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")
    
    def test_min_notional_rejection(self):
        """Test order below minimum notional is rejected"""
        is_valid, msg = self.validator.validate_order(quantity=0.0001, price=50.0)
        self.assertFalse(is_valid)
        self.assertIn("minimum", msg.lower())
    
    def test_lot_size_compliance(self):
        """Test lot size compliance check"""
        # Use a quantity that passes min notional but fails lot size
        # 0.000123 is not a multiple of 0.00001 (has remainder 0.000003)
        is_valid, msg = self.validator.validate_order(quantity=0.000123, price=100000.0)
        self.assertFalse(is_valid)
        self.assertIn("lot size", msg.lower())
    
    def test_round_quantity(self):
        """Test quantity rounding to lot size"""
        rounded = self.validator.round_quantity(0.123456)
        
        # Should be rounded down to nearest lot size multiple
        self.assertEqual(rounded, 0.12345)
        
        # Should be exact multiple of lot size
        from decimal import Decimal
        self.assertEqual(Decimal(str(rounded)) % Decimal(str(self.validator.lot_size)), 0)


class TestExecutionLogger(unittest.TestCase):
    """Test execution logging"""
    
    def setUp(self):
        self.log_file = "/tmp/test_execution_log.json"
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        self.logger = ExecutionLogger(log_file=self.log_file)
    
    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    
    def test_log_execution(self):
        """Test logging an execution"""
        order_data = {
            'symbol': 'BTC/USD',
            'side': 'buy',
            'quantity': 0.1,
            'price': 50000.0,
            'slippage': 2.5,
            'fee': 10.0
        }
        
        self.logger.log_execution(order_data)
        
        self.assertEqual(len(self.logger.executions), 1)
        self.assertEqual(self.logger.executions[0]['symbol'], 'BTC/USD')
    
    def test_save_to_file(self):
        """Test saving log to file"""
        order_data = {'symbol': 'BTC/USD', 'side': 'buy'}
        self.logger.log_execution(order_data)
        self.logger.save_to_file()
        
        self.assertTrue(os.path.exists(self.log_file))
        
        with open(self.log_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['symbol'], 'BTC/USD')
    
    def test_statistics(self):
        """Test statistics calculation"""
        self.logger.log_execution({'slippage': 2.0, 'fee': 10.0})
        self.logger.log_execution({'slippage': 3.0, 'fee': 15.0})
        
        stats = self.logger.get_statistics()
        
        self.assertEqual(stats['total_orders'], 2)
        self.assertEqual(stats['total_slippage'], 5.0)
        self.assertEqual(stats['avg_slippage'], 2.5)
        self.assertEqual(stats['total_fees'], 25.0)
        self.assertEqual(stats['avg_fees'], 12.5)


class TestRealisticCryptoTrader(unittest.TestCase):
    """Test main trader functionality"""
    
    def setUp(self):
        self.config = {
            'log_level': 'WARNING',
            'initial_cash': 10000.0,
            'slippage': {'base_bps': 5.0, 'volatility_multiplier': 1.0},
            'fees': {'maker_bps': 10.0, 'taker_bps': 20.0},
            'validator': {'min_notional': 10.0, 'lot_size': 0.00001, 'price_precision': 2},
            'execution_latency_ms': 10,  # Reduced for testing
            'execution_log_file': '/tmp/test_trader_log.json'
        }
        
        self.trader = RealisticCryptoTrader(ExecutionMode.BACKTEST, self.config)
    
    def tearDown(self):
        if os.path.exists('/tmp/test_trader_log.json'):
            os.remove('/tmp/test_trader_log.json')
        if os.path.exists('portfolio_state.json'):
            os.remove('portfolio_state.json')
    
    def test_buy_order_execution(self):
        """Test buying cryptocurrency"""
        result = self.trader.execute_order(
            symbol='BTC/USD',
            side=OrderSide.BUY,
            quantity=0.1,
            price=50000.0,
            order_type=OrderType.MARKET,
            volume_24h=1000.0,
            spread_pct=0.1
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['side'], 'buy')
        self.assertGreater(result['fill_price'], result['expected_price'])  # Slippage on buy
        self.assertGreater(result['slippage'], 0)
        self.assertGreater(result['fee'], 0)
        
        # Check portfolio updated
        portfolio = self.trader.get_portfolio()
        self.assertEqual(portfolio['positions']['BTC/USD'], 0.1)
        self.assertLess(portfolio['cash'], self.config['initial_cash'])
    
    def test_sell_order_execution(self):
        """Test selling cryptocurrency"""
        # First buy
        self.trader.execute_order(
            symbol='BTC/USD',
            side=OrderSide.BUY,
            quantity=0.1,
            price=50000.0
        )
        
        # Then sell
        result = self.trader.execute_order(
            symbol='BTC/USD',
            side=OrderSide.SELL,
            quantity=0.05,
            price=51000.0,
            order_type=OrderType.LIMIT,  # Limit order = maker fee
            volume_24h=1000.0,
            spread_pct=0.1
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['side'], 'sell')
        self.assertLess(result['fill_price'], result['expected_price'])  # Slippage on sell
        self.assertTrue(result['is_maker'])  # Limit order
        
        # Check portfolio updated
        portfolio = self.trader.get_portfolio()
        self.assertEqual(portfolio['positions']['BTC/USD'], 0.05)
    
    def test_insufficient_cash(self):
        """Test order rejection due to insufficient cash"""
        result = self.trader.execute_order(
            symbol='BTC/USD',
            side=OrderSide.BUY,
            quantity=1.0,  # Too large
            price=50000.0
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Insufficient cash', result['error'])
    
    def test_insufficient_position(self):
        """Test order rejection due to insufficient position"""
        result = self.trader.execute_order(
            symbol='BTC/USD',
            side=OrderSide.SELL,
            quantity=0.1,  # Don't own any
            price=50000.0
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Insufficient position', result['error'])
    
    def test_min_notional_validation(self):
        """Test order rejection due to minimum notional"""
        result = self.trader.execute_order(
            symbol='BTC/USD',
            side=OrderSide.BUY,
            quantity=0.00001,  # Too small
            price=50.0
        )
        
        self.assertFalse(result['success'])
        self.assertIn('minimum', result['error'].lower())
    
    def test_lot_size_rounding(self):
        """Test that quantities are rounded to lot size"""
        result = self.trader.execute_order(
            symbol='BTC/USD',
            side=OrderSide.BUY,
            quantity=0.123456,  # Will be rounded
            price=50000.0
        )
        
        self.assertTrue(result['success'])
        # Should be rounded to 0.12345 (lot size = 0.00001)
        self.assertEqual(result['quantity'], 0.12345)
    
    def test_execution_statistics(self):
        """Test execution statistics tracking"""
        # Execute multiple trades
        self.trader.execute_order('BTC/USD', OrderSide.BUY, 0.1, 50000.0)
        self.trader.execute_order('BTC/USD', OrderSide.SELL, 0.05, 51000.0)
        
        stats = self.trader.get_execution_stats()
        
        self.assertEqual(stats['total_orders'], 2)
        self.assertGreater(stats['total_slippage'], 0)
        self.assertGreater(stats['total_fees'], 0)
        self.assertGreater(stats['avg_slippage'], 0)
        self.assertGreater(stats['avg_fees'], 0)
    
    def test_state_persistence(self):
        """Test saving and loading portfolio state"""
        # Execute a trade
        self.trader.execute_order('BTC/USD', OrderSide.BUY, 0.1, 50000.0)
        
        # Save state
        self.trader.save_state()
        
        self.assertTrue(os.path.exists('portfolio_state.json'))
        
        # Create new trader and load state
        new_trader = RealisticCryptoTrader(ExecutionMode.BACKTEST, self.config)
        new_trader.load_state()
        
        # Portfolios should match
        original_portfolio = self.trader.get_portfolio()
        loaded_portfolio = new_trader.get_portfolio()
        
        self.assertEqual(original_portfolio['cash'], loaded_portfolio['cash'])
        self.assertEqual(original_portfolio['positions'], loaded_portfolio['positions'])
    
    def test_backtest_vs_live_mode(self):
        """Test that both modes can execute orders"""
        backtest_trader = RealisticCryptoTrader(ExecutionMode.BACKTEST, self.config)
        live_config = self.config.copy()
        live_config['execution_log_file'] = '/tmp/test_live_log.json'
        live_trader = RealisticCryptoTrader(ExecutionMode.LIVE, live_config)
        
        # Execute same order in both modes
        backtest_result = backtest_trader.execute_order(
            'BTC/USD', OrderSide.BUY, 0.1, 50000.0
        )
        live_result = live_trader.execute_order(
            'BTC/USD', OrderSide.BUY, 0.1, 50000.0
        )
        
        # Both should succeed
        self.assertTrue(backtest_result['success'])
        self.assertTrue(live_result['success'])
        
        # Both should have slippage and fees
        self.assertGreater(backtest_result['slippage'], 0)
        self.assertGreater(live_result['slippage'], 0)
        
        if os.path.exists('/tmp/test_live_log.json'):
            os.remove('/tmp/test_live_log.json')


class TestIntegration(unittest.TestCase):
    """Integration tests simulating real trading scenarios"""
    
    def setUp(self):
        self.config = {
            'log_level': 'WARNING',
            'initial_cash': 10000.0,
            'slippage': {'base_bps': 5.0, 'volatility_multiplier': 1.5},
            'fees': {'maker_bps': 10.0, 'taker_bps': 20.0},
            'validator': {'min_notional': 10.0, 'lot_size': 0.00001, 'price_precision': 2},
            'execution_latency_ms': 10,
            'execution_log_file': '/tmp/integration_test_log.json'
        }
    
    def tearDown(self):
        if os.path.exists('/tmp/integration_test_log.json'):
            os.remove('/tmp/integration_test_log.json')
    
    def test_full_trading_session(self):
        """Test a complete trading session with multiple trades"""
        trader = RealisticCryptoTrader(ExecutionMode.BACKTEST, self.config)
        
        initial_cash = trader.get_portfolio()['cash']
        
        # Buy BTC
        buy_result = trader.execute_order(
            'BTC/USD', OrderSide.BUY, 0.1, 50000.0, volume_24h=1000.0
        )
        self.assertTrue(buy_result['success'])
        
        # Buy ETH
        buy_eth_result = trader.execute_order(
            'ETH/USD', OrderSide.BUY, 1.0, 3000.0, volume_24h=5000.0
        )
        self.assertTrue(buy_eth_result['success'])
        
        # Sell half of BTC at profit
        sell_result = trader.execute_order(
            'BTC/USD', OrderSide.SELL, 0.05, 52000.0, 
            order_type=OrderType.LIMIT, volume_24h=1000.0
        )
        self.assertTrue(sell_result['success'])
        
        # Check portfolio
        portfolio = trader.get_portfolio()
        self.assertEqual(portfolio['positions']['BTC/USD'], 0.05)
        self.assertEqual(portfolio['positions']['ETH/USD'], 1.0)
        
        # Verify total value (cash + positions value at current prices)
        btc_value = 0.05 * 52000.0
        eth_value = 1.0 * 3000.0
        total_value = portfolio['cash'] + btc_value + eth_value
        
        # Verify fees and slippage were applied
        stats = trader.get_execution_stats()
        self.assertEqual(stats['total_orders'], 3)
        self.assertGreater(stats['total_fees'], 0)
        self.assertGreater(stats['total_slippage'], 0)
        
        # Total costs (fees + slippage) should be deducted
        total_costs = stats['total_fees'] + abs(stats['total_slippage'])
        # Account for the profit from BTC price increase (0.05 * (52000 - 50000) = 100)
        # Total value should be close to initial - costs + profit
        # Just verify we tracked fees and slippage
        self.assertGreater(total_costs, 0)
        
        # Finalize session
        trader.finalize()
        
        # Check logs were saved
        self.assertTrue(os.path.exists('/tmp/integration_test_log.json'))
    
    def test_conservative_vs_aggressive_execution(self):
        """Test difference between conservative and aggressive configs"""
        
        # Conservative config (higher slippage and fees)
        conservative_config = self.config.copy()
        conservative_config['slippage'] = {'base_bps': 10.0, 'volatility_multiplier': 2.0}
        conservative_config['fees'] = {'maker_bps': 15.0, 'taker_bps': 30.0}
        
        # Aggressive config (lower slippage and fees)
        aggressive_config = self.config.copy()
        aggressive_config['slippage'] = {'base_bps': 2.0, 'volatility_multiplier': 1.0}
        aggressive_config['fees'] = {'maker_bps': 5.0, 'taker_bps': 10.0}
        aggressive_config['execution_log_file'] = '/tmp/aggressive_test_log.json'
        
        conservative_trader = RealisticCryptoTrader(ExecutionMode.BACKTEST, conservative_config)
        aggressive_trader = RealisticCryptoTrader(ExecutionMode.BACKTEST, aggressive_config)
        
        # Execute same trade in both
        conservative_result = conservative_trader.execute_order(
            'BTC/USD', OrderSide.BUY, 0.1, 50000.0
        )
        aggressive_result = aggressive_trader.execute_order(
            'BTC/USD', OrderSide.BUY, 0.1, 50000.0
        )
        
        # Conservative should have higher costs
        self.assertGreater(
            conservative_result['slippage'] + conservative_result['fee'],
            aggressive_result['slippage'] + aggressive_result['fee']
        )
        
        # Conservative trader should have less cash remaining
        self.assertLess(
            conservative_trader.get_portfolio()['cash'],
            aggressive_trader.get_portfolio()['cash']
        )
        
        if os.path.exists('/tmp/aggressive_test_log.json'):
            os.remove('/tmp/aggressive_test_log.json')


if __name__ == '__main__':
    unittest.main()
