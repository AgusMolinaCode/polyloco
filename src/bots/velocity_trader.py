"""
Velocity Trader - Estrategia de Alta Velocidad
Solo Fast Loop 5-15 minutos para BTC, ETH, SOL
"""
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests

from src.trading.simmer_client import SimmerTrader


@dataclass
class VelocityOpportunity:
    """Oportunidad de velocidad"""
    market_id: str
    asset: str  # BTC, ETH, SOL
    side: str
    entry_price: float
    cex_price: float
    divergence: float  # Diferencia entre CEX y Polymarket
    expected_profit: float
    speed_score: float  # Qué tan rápido debemos actuar


class VelocityTrader:
    """
    Trader de alta velocidad
    - Escanea cada 5 segundos
    - BTC, ETH, SOL simultáneos
    - Aprovecha ventana de 5-15ms
    """
    
    def __init__(self):
        self.trader = SimmerTrader()
        self.assets = ["BTC", "ETH", "SOL"]
        self.scan_interval = 5  # 5 segundos
        self.min_divergence = 0.005  # 0.5% mínimo
        self.max_latency = 0.015  # 15ms máximo
        
        # Fees
        self.fast_fee = 0.10  # 10%
        
        print("⚡ Velocity Trader inicializado")
        print(f"🎯 Assets: {', '.join(self.assets)}")
        print(f"⏱️  Scan interval: {self.scan_interval}s")
    
    def get_cex_prices(self) -> Dict[str, float]:
        """Obtener precios de Binance en tiempo real"""
        prices = {}
        
        try:
            # BTC
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
                timeout=2
            )
            prices["BTC"] = float(response.json()["price"])
            
            # ETH
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT",
                timeout=2
            )
            prices["ETH"] = float(response.json()["price"])
            
            # SOL
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT",
                timeout=2
            )
            prices["SOL"] = float(response.json()["price"])
            
        except Exception as e:
            print(f"Error obteniendo precios CEX: {e}")
        
        return prices
    
    def get_polymarket_price(self, asset: str) -> Optional[float]:
        """Obtener precio de Polymarket"""
        try:
            markets = self.trader.get_markets(status="active", limit=50)
            
            for market in markets:
                question = getattr(market, 'question', '').lower()
                if asset.lower() in question:
                    if "5 minute" in question or "15 minute" in question:
                        return getattr(market, 'current_probability', None)
            
        except Exception as e:
            print(f"Error obteniendo precio Polymarket: {e}")
        
        return None
    
    def calculate_divergence(
        self,
        cex_price: float,
        pm_price: float,
        asset: str
    ) -> float:
        """Calcular divergencia entre CEX y Polymarket"""
        # Normalizar precios (ambos deberían estar entre 0-1 para up/down)
        # Esto es una simplificación, en realidad necesitaríamos más lógica
        return abs(cex_price - pm_price) / pm_price
    
    def find_opportunities(self) -> List[VelocityOpportunity]:
        """Buscar oportunidades de velocidad"""
        opportunities = []
        
        start_time = time.time()
        
        # Obtener precios CEX
        cex_prices = self.get_cex_prices()
        
        for asset in self.assets:
            if asset not in cex_prices:
                continue
            
            cex_price = cex_prices[asset]
            pm_price = self.get_polymarket_price(asset)
            
            if not pm_price:
                continue
            
            # Calcular divergencia
            divergence = self.calculate_divergence(cex_price, pm_price, asset)
            
            if divergence < self.min_divergence:
                continue
            
            # Determinar dirección
            if cex_price > pm_price:
                side = "yes"  # CEX más alto = sube
            else:
                side = "no"   # CEX más bajo = baja
            
            # Calcular profit esperado (después de fees)
            gross_profit = divergence * 100  # Aproximado
            fees = self.fast_fee * 100
            net_profit = gross_profit - fees
            
            if net_profit <= 0:
                continue
            
            # Calcular speed score (qué tan rápido debemos actuar)
            latency = time.time() - start_time
            speed_score = 1 - (latency / self.max_latency)
            speed_score = max(0, speed_score)
            
            opportunity = VelocityOpportunity(
                market_id=f"{asset.lower()}-fast",
                asset=asset,
                side=side,
                entry_price=pm_price,
                cex_price=cex_price,
                divergence=divergence,
                expected_profit=net_profit,
                speed_score=speed_score
            )
            
            opportunities.append(opportunity)
            
            print(f"⚡ {asset}: Divergencia {divergence:.2%}")
            print(f"   CEX: ${cex_price:.2f} | PM: ${pm_price:.2f}")
            print(f"   Side: {side.upper()} | Profit: ${net_profit:.2f}")
            print(f"   Speed: {speed_score:.1%}")
        
        return opportunities
    
    async def execute_trade(self, opp: VelocityOpportunity) -> bool:
        """Ejecutar trade de velocidad"""
        try:
            # Verificar balance
            balance = self.trader.get_balance()
            if balance < 2.0:
                print(f"❌ Balance insuficiente: ${balance:.2f}")
                return False
            
            # Monto fijo para velocidad
            amount = 2.0
            
            # Ejecutar
            result = self.trader.trade(
                market_id=opp.market_id,
                side=opp.side,
                amount=amount,
                reasoning=f"Velocity: {opp.asset} divergence {opp.divergence:.2%}"
            )
            
            if result.get("success"):
                print(f"✅ Trade ejecutado: {opp.asset} {opp.side.upper()}")
                return True
            else:
                print(f"❌ Trade fallido: {result.get('error')}")
                return False
                
        except Exception as e:
            print(f"Error ejecutando trade: {e}")
            return False
    
    async def run_velocity_loop(self):
        """Loop principal de velocidad"""
        print("🚀 Iniciando Velocity Loop...")
        
        while True:
            try:
                start = time.time()
                
                # Buscar oportunidades
                opportunities = self.find_opportunities()
                
                if opportunities:
                    # Ordenar por speed score
                    opportunities.sort(key=lambda x: x.speed_score, reverse=True)
                    
                    # Ejecutar el mejor
                    best = opportunities[0]
                    if best.speed_score > 0.5:  # Solo si hay tiempo suficiente
                        await self.execute_trade(best)
                
                # Calcular tiempo restante
                elapsed = time.time() - start
                sleep_time = max(0, self.scan_interval - elapsed)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                
            except Exception as e:
                print(f"Error en loop: {e}")
                await asyncio.sleep(5)


def main():
    """Ejecutar Velocity Trader"""
    trader = VelocityTrader()
    
    # Mostrar balance inicial
    balance = trader.trader.get_balance()
    print(f"💰 Balance inicial: ${balance:.2f}")
    print()
    
    # Iniciar loop
    asyncio.run(trader.run_velocity_loop())


if __name__ == "__main__":
    main()
