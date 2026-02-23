"""
Configuración de canales de Discord para cada bot
"""
import os
from dataclasses import dataclass


@dataclass
class DiscordChannels:
    """IDs de canales de Discord"""
    
    # Canales principales
    balance: int = 0
    trades: int = 0
    positions: int = 0
    alerts: int = 0
    stats: int = 0
    
    # Canales de bots
    elon: int = 0
    fast_loop: int = 0
    mert: int = 0
    signal: int = 0
    weather: int = 0
    
    @classmethod
    def from_env(cls) -> "DiscordChannels":
        """Cargar desde variables de entorno"""
        return cls(
            balance=int(os.getenv("DISCORD_CHANNEL_BALANCE", "0")),
            trades=int(os.getenv("DISCORD_CHANNEL_TRADES", "0")),
            positions=int(os.getenv("DISCORD_CHANNEL_POSITIONS", "0")),
            alerts=int(os.getenv("DISCORD_CHANNEL_ALERTS", "0")),
            stats=int(os.getenv("DISCORD_CHANNEL_STATS", "0")),
            elon=int(os.getenv("DISCORD_CHANNEL_ELON", "0")),
            fast_loop=int(os.getenv("DISCORD_CHANNEL_FAST", "0")),
            mert=int(os.getenv("DISCORD_CHANNEL_MERT", "0")),
            signal=int(os.getenv("DISCORD_CHANNEL_SIGNAL", "0")),
            weather=int(os.getenv("DISCORD_CHANNEL_WEATHER", "0")),
        )
