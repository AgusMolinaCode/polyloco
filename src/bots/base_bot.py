"""
Base Bot - Clase base para todos los bots de trading
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging
from datetime import datetime
from src.trading.simmer_client import SimmerTrader
from src.config.settings import config


class BaseBot(ABC):
    """Clase base para bots de trading"""
    
    def __init__(self, name: str, source_tag: str):
        self.name = name
        self.source_tag = source_tag
        self.trader = SimmerTrader()
        self.logger = self._setup_logger()
        self.trades_executed = 0
        self.trades_failed = 0
    
    def _setup_logger(self) -> logging.Logger:
        """Configurar logger"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.INFO)
        
        # Handler para archivo
        fh = logging.FileHandler(f"logs/{self.name.lower()}.log")
        fh.setLevel(logging.INFO)
        
        # Handler para consola
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    @abstractmethod
    def find_opportunities(self) -> List[Dict[str, Any]]:
        """Buscar oportunidades de trading"""
        pass
    
    @abstractmethod
    def evaluate_opportunity(self, opportunity: Dict[str, Any]) -> bool:
        """Evaluar si una oportunidad es válida"""
        pass
    
    def execute_trade(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar trade"""
        market_id = opportunity.get("market_id")
        side = opportunity.get("side", "yes")
        amount = opportunity.get("amount", config.trading.max_position_usd)
        
        # Asegurar mínimo
        amount = max(amount, config.trading.min_position_usd)
        
        result = self.trader.trade(
            market_id=market_id,
            side=side,
            amount=amount,
            reasoning=opportunity.get("reasoning", ""),
        )
        
        if result.get("success"):
            self.trades_executed += 1
            self.logger.info(f"✅ Trade exitoso: {market_id} - ${amount}")
        else:
            self.trades_failed += 1
            self.logger.error(f"❌ Trade fallido: {market_id} - {result.get('error')}")
        
        return result
    
    def run(self, dry_run: bool = True) -> Dict[str, Any]:
        """Ejecutar ciclo del bot"""
        self.logger.info(f"🚀 Iniciando {self.name}")
        
        # Verificar balance
        balance = self.trader.get_balance()
        self.logger.info(f"💰 Balance disponible: ${balance:.2f}")
        
        if balance <= 0:
            self.logger.warning("❌ Sin balance disponible")
            return {"status": "no_balance", "trades": 0}
        
        # Buscar oportunidades
        opportunities = self.find_opportunities()
        self.logger.info(f"🔍 {len(opportunities)} oportunidades encontradas")
        
        trades = 0
        for opp in opportunities:
            if self.evaluate_opportunity(opp):
                if dry_run:
                    self.logger.info(f"[DRY RUN] Trade: {opp}")
                else:
                    result = self.execute_trade(opp)
                    if result.get("success"):
                        trades += 1
                
                # Limitar trades por ciclo
                if trades >= config.trading.max_trades_per_run:
                    break
        
        return {
            "status": "success",
            "trades": trades,
            "opportunities": len(opportunities),
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del bot"""
        return {
            "name": self.name,
            "trades_executed": self.trades_executed,
            "trades_failed": self.trades_failed,
            "last_run": datetime.now().isoformat(),
        }
