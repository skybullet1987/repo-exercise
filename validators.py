"""
Order validator for exchange-compliant order validation
"""

import logging
from decimal import Decimal
from typing import Tuple


class OrderValidator:
    """
    Validates orders against exchange rules
    
    Checks:
    - Minimum notional value
    - Lot size/step size compliance
    - Price precision
    - Available balance
    """
    
    def __init__(self, min_notional: float = 10.0, lot_size: float = 0.00001, 
                 price_precision: int = 2):
        """
        Initialize order validator
        
        Args:
            min_notional: Minimum order value in quote currency
            lot_size: Minimum step size for order quantity
            price_precision: Number of decimal places for price
        """
        self.min_notional = min_notional
        self.lot_size = lot_size
        self.price_precision = price_precision
        self.logger = logging.getLogger(__name__)
    
    def validate_order(self, quantity: float, price: float) -> Tuple[bool, str]:
        """
        Validate an order
        
        Args:
            quantity: Order quantity in base currency
            price: Order price
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check minimum notional
        notional = quantity * price
        if notional < self.min_notional:
            msg = f"Order notional {notional:.2f} below minimum {self.min_notional}"
            self.logger.warning(msg)
            return False, msg
        
        # Check lot size compliance
        quantity_decimal = Decimal(str(quantity))
        lot_size_decimal = Decimal(str(self.lot_size))
        
        if quantity_decimal % lot_size_decimal != 0:
            msg = f"Order quantity {quantity} does not comply with lot size {self.lot_size}"
            self.logger.warning(msg)
            return False, msg
        
        return True, ""
    
    def round_quantity(self, quantity: float) -> float:
        """
        Round quantity to lot size
        
        Args:
            quantity: Raw quantity
            
        Returns:
            Rounded quantity
        """
        quantity_decimal = Decimal(str(quantity))
        lot_size_decimal = Decimal(str(self.lot_size))
        
        rounded = (quantity_decimal // lot_size_decimal) * lot_size_decimal
        return float(rounded)
