"""
Fast Loop Micro Trader
Enfocado en micro ganancias 5-15 minutos con cálculo de fees
"""
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests

from src.bots.base_bot import BaseBot
from src.config.settings import config


@dataclass
class TradeOpportunity:
    """Oportunidad de trade con cálculo de fees"""
    market_id: str
    market_name: str
    side: str
    entry_price: float
    target_price: float
    stop_loss: float
    amount: float
    expected_profit: float
    fees: float
    net_profit: float
    confidence: float
    time_horizon: str  # "5min" o "15min"


class FastLoopMicroTrader(BaseBot):
    """
    Fast Loop enfocado en micro ganancias
    - Trades 5-15 minutos
    - Cálculo de fees incluido
    - Múltiples trades pequeños
    """
    
    def __init__(self):
        super().__init__(
            name="FastLoopMicro",
            source_tag="fastloop:micro"
        )
        
        # Configuración micro ganancias
        self.min_momentum = 0.30  # 0.30% mínimo
        self.profit_target = 0.05  # 5% ganancia
        self.stop_loss = 0.03  # 3% pérdida
        self.max_position = 2.00  # $2 por trade
        self.check_interval = 30  # 30 segundos
        
        # Fees
        self.fast_fee = 0.10  # 10% fee fast markets
        self.min_profit_after_fees = 0.01  # 1% mínimo neto
        
        self.logger.info("🚀 FastLoop Micro Trader inicializado")
    
    def get_btc_price(self) -> Tuple[float, float]:
        """Obtener precio de BTC de Binance"""
        try:
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT",
                timeout=5
            )
            data = response.json()
            
            current_price = float(data["lastPrice"])
            price_change_pct = float(data["priceChangePercent"])
            
            return current_price, price_change_pct
        except Exception as e:
            self.logger.error(f"Error obteniendo BTC price: {e}")
            return 0, 0
    
    def calculate_fees(self, amount: float, is_fast_market: bool = True) -> float:
        """Calcular fees de Polymarket"""
        fee_pct = self.fast_fee if is_fast_market else 0.02
        return amount * fee_pct
    
    def calculate_net_profit(
        self,
        entry_price: float,
        exit_price: float,
        amount: float,
        is_fast_market: bool = True
    ) -> Tuple[float, float]:
        """
        Calcular ganancia neta después de fees
        Retorna: (ganancia_bruta, ganancia_neta)
        """
        # Ganancia bruta
        shares = amount / entry_price
        exit_value = shares * exit_price
        gross_profit = exit_value - amount
        
        # Fees (entrada + salida)
        entry_fee = self.calculate_fees(amount, is_fast_market)
        exit_fee = self.calculate_fees(exit_value, is_fast_market)
        total_fees = entry_fee + exit_fee
        
        # Ganancia neta
        net_profit = gross_profit - total_fees
        
        return gross_profit, net_profit
    
    def is_profitable_after_fees(
        self,
        entry_price: float,
        target_price: float,
        amount: float
    ) -> bool:
        """Verificar si el trade es rentable después de fees"""
        gross, net = self.calculate_net_profit(entry_price, target_price, amount)
        
        # Mínimo 1% de ganancia neta
        min_profit = amount * self.min_profit_after_fees
        
        return net >= min_profit
    
    def find_opportunities(self) -> List[Dict]:
        """Buscar oportunidades de Fast Loop"""
        opportunities = []
        
        # Obtener precio BTC
        btc_price, momentum = self.get_btc_price()
        
        if abs(momentum) < self.min_momentum:
            self.logger.info(f"Momentum {momentum:.3f}% < {self.min_momentum}%")
            return opportunities
        
        # Buscar mercados fast de BTC (sin query, filtrar después)
        markets = self.trader.get_markets(status="active", limit=100)
        
        # Filtrar solo mercados de Bitcoin
        btc_markets = []
        for market in markets:
            question = getattr(market, 'question', '').lower()
            if "bitcoin" in question or "btc" in question:
                if "5 minute" in question or "15 minute" in question:
                    btc_markets.append(market)
        
        markets = btc_markets
        
        for market in markets:
            # Solo mercados 5min o 15min
            if "5 minute" not in market.get("question", "").lower() and \
               "15 minute" not in market.get("question", "").lower():
                continue
            
            current_price = market.get("current_probability", 0.5)
            
            # Determinar dirección basada en momentum
            if momentum > 0:
                side = "yes"  # BTC sube
                target_price = min(current_price + self.profit_target, 0.95)
            else:
                side = "no"   # BTC baja
                target_price = max(current_price - self.profit_target, 0.05)
            
            # Calcular si es rentable después de fees
            amount = min(self.max_position, self.trader.get_balance() * 0.1)
            
            if amount < 1.00:
                continue
            
            gross_profit, net_profit = self.calculate_net_profit(
                current_price, target_price, amount
            )
            
            if net_profit <= 0:
                self.logger.info(f"Trade no rentable después de fees: ${net_profit:.2f}")
                continue
            
            opportunity = {
                "market_id": getattr(market, "market_id", None) or getattr(market, "id", None),
                "market_name": market.get("question", "Unknown"),
                "side": side,
                "entry_price": current_price,
                "target_price": target_price,
                "stop_loss": current_price - self.stop_loss if side == "yes" else current_price + self.stop_loss,
                "amount": amount,
                "expected_profit": gross_profit,
                "fees": self.calculate_fees(amount) * 2,
                "net_profit": net_profit,
                "confidence": abs(momentum) / 0.5,  # Normalizar
                "time_horizon": "5min" if "5 minute" in market.get("question", "") else "15min",
            }
            
            opportunities.append(opportunity)
            
            self.logger.info(
                f"🎯 Oportunidad: {opportunity['market_name'][:50]}...\n"
                f"   Side: {side.upper()} | Momentum: {momentum:.2f}%\n"
                f"   Entry: ${current_price:.2f} → Target: ${target_price:.2f}\n"
                f"   Bruto: ${gross_profit:.2f} | Fees: ${opportunity['fees']:.2f} | Neto: ${net_profit:.2f}"
            )
        
        return opportunities
    
    def evaluate_opportunity(self, opportunity: Dict) -> bool:
        """Evaluar si ejecutar el trade"""
        # Verificar balance
        balance = self.trader.get_balance()
        if balance < opportunity["amount"]:
            self.logger.warning(f"Balance insuficiente: ${balance:.2f}")
            return False
        
        # Verificar rentabilidad neta
        if opportunity["net_profit"] <= 0:
            return False
        
        # Verificar confianza mínima
        if opportunity["confidence"] < 0.5:
            return False
        
        return True
    
    async def run_micro_loop(self):
        """Loop continuo para micro trades"""
        while True:
            try:
                self.logger.info("🔍 Escaneando oportunidades Fast Loop...")
                
                result = self.run(dry_run=False)
                
                if result["trades"] > 0:
                    self.logger.info(f"✅ {result['trades']} trades ejecutados")
                
                # Esperar antes del próximo scan
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error en loop: {e}")
                await asyncio.sleep(60)  # Esperar 1 min en error


def main():
    """Ejecutar Fast Loop Micro Trader"""
    trader = FastLoopMicroTrader()
    
    # Verificar configuración
    balance = trader.trader.get_balance()
    trader.logger.info(f"💰 Balance disponible: ${balance:.2f}")
    trader.logger.info(f"🎯 Profit target: {trader.profit_target*100:.0f}%")
    trader.logger.info(f"🛑 Stop loss: {trader.stop_loss*100:.0f}%")
    trader.logger.info(f"💸 Fast fee: {trader.fast_fee*100:.0f}%")
    
    # Iniciar loop
    asyncio.run(trader.run_micro_loop())


if __name__ == "__main__":
    main()
