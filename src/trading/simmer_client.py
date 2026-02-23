"""
Cliente de Simmer - Wrapper del SDK
"""
from typing import Optional, List, Dict, Any
from simmer_sdk import SimmerClient
from src.config.settings import config


class SimmerTrader:
    """Cliente de trading para Simmer/Polymarket"""
    
    def __init__(self):
        self.client = SimmerClient(
            api_key=config.simmer.api_key,
        )
        self._linked = False
    
    def link_wallet(self) -> bool:
        """Vincular wallet para trading real"""
        try:
            result = self.client.link_wallet()
            self._linked = result.get("success", False)
            return self._linked
        except Exception as e:
            print(f"Error vinculando wallet: {e}")
            return False
    
    def get_portfolio(self) -> Dict[str, Any]:
        """Obtener portfolio actual"""
        try:
            return self.client.get_portfolio()
        except Exception as e:
            print(f"Error obteniendo portfolio: {e}")
            return {}
    
    def get_positions(self) -> List[Any]:
        """Obtener posiciones abiertas"""
        try:
            return self.client.get_positions()
        except Exception as e:
            print(f"Error obteniendo posiciones: {e}")
            return []
    
    def get_markets(self, query: str = "", status: str = "active", limit: int = 100) -> List[Dict]:
        """Buscar mercados"""
        try:
            return self.client.get_markets(q=query, status=status, limit=limit)
        except Exception as e:
            print(f"Error buscando mercados: {e}")
            return []
    
    def trade(
        self,
        market_id: str,
        side: str,
        amount: float,
        order_type: str = "GTC",
        reasoning: str = "",
    ) -> Dict[str, Any]:
        """Ejecutar trade"""
        try:
            result = self.client.trade(
                market_id=market_id,
                side=side,
                amount=amount,
                order_type=order_type,
                reasoning=reasoning,
            )
            return {
                "success": result.success,
                "trade_id": result.trade_id,
                "shares_bought": result.shares_bought,
                "error": result.error,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_balance(self) -> float:
        """Obtener balance disponible"""
        portfolio = self.get_portfolio()
        balance = portfolio.get("balance_usdc", 0)
        exposure = portfolio.get("total_exposure", 0)
        return balance - exposure
