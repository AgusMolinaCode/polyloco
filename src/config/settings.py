"""
PolyLoco - Configuración global
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class SimmerConfig:
    """Configuración de Simmer API"""
    api_key: str
    wallet_private_key: str
    base_url: str = "https://api.simmer.markets"
    
    @classmethod
    def from_env(cls) -> "SimmerConfig":
        return cls(
            api_key=os.getenv("SIMMER_API_KEY", ""),
            wallet_private_key=os.getenv("WALLET_PRIVATE_KEY", ""),
        )


@dataclass
class DiscordConfig:
    """Configuración de Discord"""
    webhook_url: str
    
    @classmethod
    def from_env(cls) -> "DiscordConfig":
        return cls(
            webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""),
        )


@dataclass
class TradingConfig:
    """Configuración de trading"""
    # Límites
    max_position_usd: float = 1.0
    max_trades_per_run: int = 3
    daily_budget: float = 10.0
    
    # Diversificación
    diversification_enabled: bool = True
    max_positions_per_market_type: int = 1
    
    # Safeguards
    slippage_max_pct: float = 0.05
    min_position_usd: float = 1.0
    
    @classmethod
    def from_env(cls) -> "TradingConfig":
        return cls(
            max_position_usd=float(os.getenv("MAX_POSITION_USD", "1.0")),
            max_trades_per_run=int(os.getenv("MAX_TRADES_PER_RUN", "3")),
            daily_budget=float(os.getenv("DAILY_BUDGET", "10.0")),
        )


class Config:
    """Configuración global de la aplicación"""
    
    def __init__(self):
        self.simmer = SimmerConfig.from_env()
        self.discord = DiscordConfig.from_env()
        self.trading = TradingConfig.from_env()
        
    def validate(self) -> bool:
        """Validar configuración mínima"""
        if not self.simmer.api_key:
            raise ValueError("SIMMER_API_KEY no configurado")
        if not self.simmer.wallet_private_key:
            raise ValueError("WALLET_PRIVATE_KEY no configurado")
        return True


# Instancia global
config = Config()
