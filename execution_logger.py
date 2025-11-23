"""
Execution logger for comprehensive order execution tracking
"""

import logging
import json
from datetime import datetime
from typing import Dict, List


class ExecutionLogger:
    """
    Comprehensive logging for order execution
    
    Tracks:
    - Expected vs actual fill prices
    - Latency metrics
    - Slippage and fees
    - Success/failure rates
    """
    
    def __init__(self, log_file: str = "execution_log.json"):
        """
        Initialize execution logger
        
        Args:
            log_file: Path to JSON log file
        """
        self.log_file = log_file
        self.executions: List[Dict] = []
        self.logger = logging.getLogger(__name__)
    
    def log_execution(self, order_data: Dict):
        """
        Log an order execution
        
        Args:
            order_data: Dictionary containing order details
        """
        order_data['timestamp'] = datetime.now().isoformat()
        self.executions.append(order_data)
        
        self.logger.info(f"Order executed: {order_data}")
    
    def save_to_file(self):
        """Save execution log to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.executions, f, indent=2)
            self.logger.info(f"Execution log saved to {self.log_file}")
        except Exception as e:
            self.logger.error(f"Failed to save execution log: {e}")
    
    def get_statistics(self) -> Dict:
        """
        Calculate execution statistics
        
        Returns:
            Dictionary of statistics
        """
        if not self.executions:
            return {}
        
        total_slippage = sum(e.get('slippage', 0) for e in self.executions)
        total_fees = sum(e.get('fee', 0) for e in self.executions)
        total_orders = len(self.executions)
        
        return {
            'total_orders': total_orders,
            'total_slippage': total_slippage,
            'avg_slippage': total_slippage / total_orders if total_orders > 0 else 0,
            'total_fees': total_fees,
            'avg_fees': total_fees / total_orders if total_orders > 0 else 0,
        }
