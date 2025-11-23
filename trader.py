"""
RealisticCryptoTrader - Main trading algorithm with realistic backtest/live parity

This implementation addresses common issues that cause discrepancy between backtest and live performance:
1. Realistic slippage modeling
2. Accurate fee calculations (maker/taker)
3. Minimum notional and lot size enforcement
4. Order execution latency simulation
5. Comprehensive logging for performance comparison
6. State persistence for portfolio synchronization
"""

import logging
import time
import json
from datetime import datetime
from typing import Dict, Optional

from trading_types import ExecutionMode, OrderType, OrderSide
from models import SlippageModel, FeeModel
from validators import OrderValidator
from execution_logger import ExecutionLogger


class RealisticCryptoTrader:
    """
    Main trading algorithm with realistic backtest and live trading support
    
    Key features:
    - Separate execution paths for backtest and live
    - Realistic slippage and fee modeling
    - Order validation and lot size enforcement
    - Comprehensive execution logging
    - Configurable execution modes (conservative/aggressive)
    """
    
    def __init__(self, mode: ExecutionMode, config: Optional[Dict] = None):
        """
        Initialize RealisticCryptoTrader
        
        Args:
            mode: Execution mode (BACKTEST or LIVE)
            config: Configuration dictionary
        """
        self.mode = mode
        self.config = config or {}
        
        # Setup logging
        log_level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        slippage_config = self.config.get('slippage', {})
        self.slippage_model = SlippageModel(
            base_slippage_bps=slippage_config.get('base_bps', 5.0),
            volatility_multiplier=slippage_config.get('volatility_multiplier', 1.0)
        )
        
        fee_config = self.config.get('fees', {})
        self.fee_model = FeeModel(
            maker_fee_bps=fee_config.get('maker_bps', 10.0),
            taker_fee_bps=fee_config.get('taker_bps', 20.0)
        )
        
        validator_config = self.config.get('validator', {})
        self.order_validator = OrderValidator(
            min_notional=validator_config.get('min_notional', 10.0),
            lot_size=validator_config.get('lot_size', 0.00001),
            price_precision=validator_config.get('price_precision', 2)
        )
        
        self.execution_logger = ExecutionLogger(
            log_file=self.config.get('execution_log_file', 'execution_log.json')
        )
        
        # Portfolio state
        self.portfolio = {
            'cash': self.config.get('initial_cash', 10000.0),
            'positions': {}
        }
        
        # Execution latency (ms)
        self.execution_latency_ms = self.config.get('execution_latency_ms', 100)
        
        self.logger.info(f"RealisticCryptoTrader initialized in {mode.value} mode")
    
    def execute_order(self, symbol: str, side: OrderSide, quantity: float, 
                     price: float, order_type: OrderType = OrderType.MARKET,
                     volume_24h: float = 1000000.0, spread_pct: float = 0.1) -> Dict:
        """
        Execute a trading order
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTC/USD')
            side: Order side (BUY or SELL)
            quantity: Order quantity in base currency
            price: Current market price
            order_type: Order type (MARKET or LIMIT)
            volume_24h: 24-hour trading volume (for slippage calculation)
            spread_pct: Bid-ask spread percentage
            
        Returns:
            Dictionary with execution results
        """
        self.logger.info(f"Executing {side.value} order: {quantity} {symbol} @ {price}")
        
        # Round quantity to lot size
        quantity = self.order_validator.round_quantity(quantity)
        
        # Validate order
        is_valid, error_msg = self.order_validator.validate_order(quantity, price)
        if not is_valid:
            return {
                'success': False,
                'error': error_msg,
                'symbol': symbol,
                'side': side.value,
                'quantity': quantity,
                'price': price
            }
        
        # Simulate execution latency in both modes
        if self.mode == ExecutionMode.BACKTEST:
            # In backtest, simulate latency
            time.sleep(self.execution_latency_ms / 1000.0)
        elif self.mode == ExecutionMode.LIVE:
            # In live mode, actual latency occurs naturally
            pass
        
        # Calculate slippage
        slippage = self.slippage_model.calculate_slippage(
            price, quantity, volume_24h, spread_pct
        )
        
        # Adjust fill price based on slippage
        if side == OrderSide.BUY:
            fill_price = price + (slippage / quantity)
        else:
            fill_price = price - (slippage / quantity)
        
        # Calculate notional value
        notional = quantity * fill_price
        
        # Calculate fees (market orders are taker, limit orders can be maker)
        is_maker = order_type == OrderType.LIMIT
        fee = self.fee_model.calculate_fee(notional, is_maker)
        
        # Calculate total cost/proceeds
        if side == OrderSide.BUY:
            total_cost = notional + fee
            
            # Check balance
            if total_cost > self.portfolio['cash']:
                return {
                    'success': False,
                    'error': f'Insufficient cash: need {total_cost:.2f}, have {self.portfolio["cash"]:.2f}',
                    'symbol': symbol,
                    'side': side.value,
                    'quantity': quantity,
                    'price': price
                }
            
            # Update portfolio
            self.portfolio['cash'] -= total_cost
            if symbol not in self.portfolio['positions']:
                self.portfolio['positions'][symbol] = 0.0
            self.portfolio['positions'][symbol] += quantity
            
        else:  # SELL
            # Check position
            current_position = self.portfolio['positions'].get(symbol, 0.0)
            if quantity > current_position:
                return {
                    'success': False,
                    'error': f'Insufficient position: need {quantity}, have {current_position}',
                    'symbol': symbol,
                    'side': side.value,
                    'quantity': quantity,
                    'price': price
                }
            
            # Update portfolio
            proceeds = notional - fee
            self.portfolio['cash'] += proceeds
            self.portfolio['positions'][symbol] -= quantity
        
        # Log execution
        execution_data = {
            'mode': self.mode.value,
            'symbol': symbol,
            'side': side.value,
            'order_type': order_type.value,
            'quantity': quantity,
            'expected_price': price,
            'fill_price': fill_price,
            'slippage': slippage,
            'slippage_bps': (abs(fill_price - price) / price) * 10000,
            'fee': fee,
            'notional': notional,
            'is_maker': is_maker,
            'success': True
        }
        
        self.execution_logger.log_execution(execution_data)
        
        self.logger.info(f"Order executed successfully: filled @ {fill_price:.2f}, "
                        f"slippage={slippage:.4f}, fee={fee:.4f}")
        
        return execution_data
    
    def get_portfolio(self) -> Dict:
        """
        Get current portfolio state
        
        Returns:
            Portfolio dictionary
        """
        return self.portfolio.copy()
    
    def get_execution_stats(self) -> Dict:
        """
        Get execution statistics
        
        Returns:
            Statistics dictionary
        """
        return self.execution_logger.get_statistics()
    
    def save_state(self, filepath: str = "portfolio_state.json"):
        """
        Save portfolio state to file
        
        Args:
            filepath: Path to save state
        """
        try:
            state = {
                'portfolio': self.portfolio,
                'mode': self.mode.value,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            self.logger.info(f"Portfolio state saved to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save portfolio state: {e}")
    
    def load_state(self, filepath: str = "portfolio_state.json"):
        """
        Load portfolio state from file
        
        Args:
            filepath: Path to load state from
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.portfolio = state['portfolio']
            self.logger.info(f"Portfolio state loaded from {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to load portfolio state: {e}")
    
    def finalize(self):
        """
        Finalize trading session and save logs
        """
        self.execution_logger.save_to_file()
        self.save_state()
        
        stats = self.get_execution_stats()
        self.logger.info(f"Trading session finalized. Statistics: {stats}")


def main():
    """Example usage of RealisticCryptoTrader"""
    
    # Configuration for conservative execution
    conservative_config = {
        'log_level': 'INFO',
        'initial_cash': 10000.0,
        'slippage': {
            'base_bps': 5.0,  # 5 basis points base slippage
            'volatility_multiplier': 1.5  # Higher for volatile markets
        },
        'fees': {
            'maker_bps': 10.0,  # 0.1% maker fee
            'taker_bps': 20.0   # 0.2% taker fee
        },
        'validator': {
            'min_notional': 10.0,
            'lot_size': 0.00001,
            'price_precision': 2
        },
        'execution_latency_ms': 100,
        'execution_log_file': 'backtest_execution_log.json'
    }
    
    # Example backtest
    print("=== BACKTEST MODE ===")
    backtest_trader = RealisticCryptoTrader(ExecutionMode.BACKTEST, conservative_config)
    
    # Execute some trades
    result1 = backtest_trader.execute_order(
        symbol='BTC/USD',
        side=OrderSide.BUY,
        quantity=0.1,
        price=50000.0,
        order_type=OrderType.MARKET,
        volume_24h=1000.0,  # BTC
        spread_pct=0.05
    )
    print(f"Trade 1: {result1}")
    
    result2 = backtest_trader.execute_order(
        symbol='BTC/USD',
        side=OrderSide.SELL,
        quantity=0.05,
        price=51000.0,
        order_type=OrderType.LIMIT,
        volume_24h=1000.0,
        spread_pct=0.05
    )
    print(f"Trade 2: {result2}")
    
    print(f"\nPortfolio: {backtest_trader.get_portfolio()}")
    print(f"Statistics: {backtest_trader.get_execution_stats()}")
    
    backtest_trader.finalize()
    
    # Example live trading (with same conservative config)
    print("\n=== LIVE MODE ===")
    live_config = conservative_config.copy()
    live_config['execution_log_file'] = 'live_execution_log.json'
    
    live_trader = RealisticCryptoTrader(ExecutionMode.LIVE, live_config)
    
    result3 = live_trader.execute_order(
        symbol='BTC/USD',
        side=OrderSide.BUY,
        quantity=0.1,
        price=50000.0,
        order_type=OrderType.MARKET,
        volume_24h=1000.0,
        spread_pct=0.05
    )
    print(f"Live Trade: {result3}")
    
    print(f"\nLive Portfolio: {live_trader.get_portfolio()}")
    print(f"Live Statistics: {live_trader.get_execution_stats()}")
    
    live_trader.finalize()


if __name__ == "__main__":
    main()
