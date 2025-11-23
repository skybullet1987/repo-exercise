"""
Slippage and Fee models for realistic trading simulation
"""

import logging


class SlippageModel:
    """
    Realistic slippage model that simulates market impact
    
    Slippage increases with:
    - Order size relative to volume
    - Market volatility
    - Spread width
    """
    
    def __init__(self, base_slippage_bps: float = 5.0, volatility_multiplier: float = 1.0):
        """
        Initialize slippage model
        
        Args:
            base_slippage_bps: Base slippage in basis points (0.01%)
            volatility_multiplier: Multiplier for high volatility periods
        """
        self.base_slippage_bps = base_slippage_bps
        self.volatility_multiplier = volatility_multiplier
        self.logger = logging.getLogger(__name__)
    
    def calculate_slippage(self, price: float, order_size: float, volume_24h: float, 
                          spread_pct: float = 0.1) -> float:
        """
        Calculate slippage for an order
        
        Args:
            price: Current market price
            order_size: Size of order in base currency
            volume_24h: 24-hour trading volume in base currency
            spread_pct: Bid-ask spread as percentage
            
        Returns:
            Slippage amount in quote currency
        """
        # Base slippage
        slippage_pct = self.base_slippage_bps / 10000.0
        
        # Add market impact based on order size vs volume
        if volume_24h > 0:
            volume_impact = (order_size / volume_24h) * 100  # As percentage
            slippage_pct += volume_impact * 0.5
        
        # Add spread contribution (spread_pct is already a percentage)
        slippage_pct += (spread_pct / 100.0) / 2  # Half spread on average
        
        # Apply volatility multiplier
        slippage_pct *= self.volatility_multiplier
        
        slippage = price * order_size * slippage_pct
        
        self.logger.debug(f"Slippage calculation: order_size={order_size}, "
                         f"volume_24h={volume_24h}, slippage_pct={slippage_pct:.4f}%, "
                         f"slippage_amount={slippage:.8f}")
        
        return slippage


class FeeModel:
    """
    Realistic fee model supporting maker/taker fees
    
    Different fee rates for:
    - Maker orders (provide liquidity)
    - Taker orders (take liquidity)
    - Different exchange tiers
    """
    
    def __init__(self, maker_fee_bps: float = 10.0, taker_fee_bps: float = 20.0):
        """
        Initialize fee model
        
        Args:
            maker_fee_bps: Maker fee in basis points (0.01%)
            taker_fee_bps: Taker fee in basis points (0.01%)
        """
        self.maker_fee_bps = maker_fee_bps
        self.taker_fee_bps = taker_fee_bps
        self.logger = logging.getLogger(__name__)
    
    def calculate_fee(self, notional_value: float, is_maker: bool = False) -> float:
        """
        Calculate trading fee
        
        Args:
            notional_value: Total value of trade in quote currency
            is_maker: Whether this is a maker order (limit order that adds liquidity)
            
        Returns:
            Fee amount in quote currency
        """
        fee_bps = self.maker_fee_bps if is_maker else self.taker_fee_bps
        fee = notional_value * (fee_bps / 10000.0)
        
        self.logger.debug(f"Fee calculation: notional={notional_value}, "
                         f"is_maker={is_maker}, fee_bps={fee_bps}, fee={fee:.8f}")
        
        return fee
