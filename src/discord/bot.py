"""
Bot de Discord para PolyLoco
"""
import asyncio
import discord
from discord.ext import commands, tasks
from datetime import datetime
from src.config.settings import config
from src.discord.channels import DiscordChannels
from src.trading.simmer_client import SimmerTrader


class PolyLocoBot(commands.Bot):
    """Bot de Discord para monitorear y controlar trading"""
    
    def __init__(self):
        # Usar intents con message_content (ahora habilitado en Discord)
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )
        
        self.trader = SimmerTrader()
        self.channels = DiscordChannels.from_env()
    
    async def setup_hook(self):
        """Setup inicial"""
        self.monitor_trades.start()
    
    async def on_ready(self):
        """Bot listo"""
        print(f"✅ {self.user} conectado")
        
        # Enviar mensaje a canal de trades
        await self.send_to_channel(
            "trades", 
            "🚀 **PolyLoco Bot activado**\n"
            "Sistema de micro ganancias iniciado\n"
            "Enfocado en Fast Loop 5-15 minutos"
        )
    
    async def send_to_channel(self, channel_type: str, message: str = "", embed=None):
        """Enviar mensaje a canal específico"""
        channel_id = getattr(self.channels, channel_type, 0)
        if not channel_id:
            print(f"⚠️ Canal {channel_type} no configurado")
            return
        
        channel = self.get_channel(channel_id)
        if not channel:
            print(f"⚠️ No se encontró canal {channel_type} (ID: {channel_id})")
            return
        
        try:
            if embed:
                await channel.send(message, embed=embed)
            else:
                await channel.send(message)
            print(f"✅ Mensaje enviado a {channel_type}")
        except Exception as e:
            print(f"❌ Error enviando a {channel_type}: {e}")
    
    async def notify_trade(self, bot_name: str, market: str, amount: float, success: bool, profit: float = None):
        """Notificar trade ejecutado"""
        color = discord.Color.green() if success else discord.Color.red()
        
        embed = discord.Embed(
            title=f"🤖 {bot_name}",
            color=color,
            timestamp=datetime.now(),
        )
        embed.add_field(name="Mercado", value=market[:100], inline=False)
        embed.add_field(name="Monto", value=f"${amount:.2f}", inline=True)
        embed.add_field(name="Estado", value="✅ Éxito" if success else "❌ Fallido", inline=True)
        
        if profit is not None:
            embed.add_field(name="Profit", value=f"${profit:.2f}", inline=True)
        
        # Enviar a canal de trades
        await self.send_to_channel("trades", "", embed)
    
    async def notify_position(self, market: str, shares: float, value: float):
        """Notificar posición actualizada"""
        embed = discord.Embed(
            title="📈 Posición Actualizada",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Mercado", value=market[:100], inline=False)
        embed.add_field(name="Shares", value=f"{shares:.2f}", inline=True)
        embed.add_field(name="Valor", value=f"${value:.2f}", inline=True)
        
        # Enviar a canal de posiciones
        await self.send_to_channel("positions", "", embed)
    
    @tasks.loop(minutes=2)
    async def monitor_trades(self):
        """Monitorear trades cada 2 minutos"""
        try:
            # Verificar balance
            portfolio = self.trader.get_portfolio()
            balance = portfolio.get("balance_usdc", 0)
            exposure = portfolio.get("total_exposure", 0)
            available = balance - exposure
            
            # Enviar a canal de balance si está bajo
            if available < 0:
                await self.send_to_channel(
                    "balance",
                    f"⚠️ **Balance bajo**\n"
                    f"Disponible: ${available:.2f}\n"
                    f"Fondear para continuar trading"
                )
            
            # Enviar estadísticas a canal de stats
            embed = discord.Embed(
                title="📊 Estadísticas",
                color=discord.Color.blue(),
                timestamp=datetime.now(),
            )
            embed.add_field(name="Balance", value=f"${balance:.2f}", inline=True)
            embed.add_field(name="Exposure", value=f"${exposure:.2f}", inline=True)
            embed.add_field(name="Disponible", value=f"${available:.2f}", inline=True)
            
            await self.send_to_channel("stats", "", embed)
            
        except Exception as e:
            print(f"Error en monitor_trades: {e}")
    
    @commands.command()
    async def balance(self, ctx):
        """Ver balance actual"""
        portfolio = self.trader.get_portfolio()
        balance = portfolio.get("balance_usdc", 0)
        exposure = portfolio.get("total_exposure", 0)
        available = balance - exposure
        
        embed = discord.Embed(
            title="💰 Balance",
            color=discord.Color.green() if available > 0 else discord.Color.red(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="USDC Total", value=f"${balance:.2f}", inline=True)
        embed.add_field(name="Exposure", value=f"${exposure:.2f}", inline=True)
        embed.add_field(name="Disponible", value=f"${available:.2f}", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def positions(self, ctx):
        """Ver posiciones abiertas"""
        positions = self.trader.get_positions()
        
        if not positions:
            await ctx.send("📊 No hay posiciones abiertas")
            return
        
        embed = discord.Embed(
            title="📈 Posiciones Abiertas",
            color=discord.Color.blue(),
        )
        
        for pos in positions[:5]:  # Mostrar máximo 5
            question = getattr(pos, 'question', 'N/A')[:50]
            shares = getattr(pos, 'shares', 0)
            embed.add_field(
                name=question + "...",
                value=f"Shares: {shares:.2f}",
                inline=False,
            )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def status(self, ctx):
        """Ver estado de los bots"""
        embed = discord.Embed(
            title="🤖 Estado de Bots",
            color=discord.Color.blue(),
            timestamp=datetime.now(),
        )
        
        bots = [
            ("Elon Tweet Trader", "🐦", "Cada 2 min", "10%"),
            ("Fast Loop", "⚡", "Cada 30s", "70%"),
            ("Mert Sniper", "🎯", "Cada 2 min", "10%"),
            ("Signal Sniper", "📡", "Cada 5 min", "10%"),
        ]
        
        for name, emoji, freq, capital in bots:
            embed.add_field(
                name=f"{emoji} {name}",
                value=f"Frecuencia: {freq}\nCapital: {capital}\nEstado: 🟢 Activo",
                inline=True,
            )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def estrategia(self, ctx):
        """Ver estrategia actual"""
        embed = discord.Embed(
            title="🎯 Estrategia: Micro Ganancias",
            description="Enfocado en Fast Loop 5-15 minutos",
            color=discord.Color.gold(),
        )
        
        embed.add_field(
            name="⚡ Fast Loop (70%)",
            value="Momentum BTC >0.30%\nProfit target: 15%\nFees: 10%",
            inline=False,
        )
        
        embed.add_field(
            name="🐦 Elon Tweets (10%)",
            value="Eventos de tweets\nHorizonte: Días",
            inline=True,
        )
        
        embed.add_field(
            name="🎯 Mert Sniper (10%)",
            value="Mercados expirando\nSplit 60/40",
            inline=True,
        )
        
        embed.add_field(
            name="📡 Signal (10%)",
            value="Noticias RSS\nKeywords",
            inline=True,
        )
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def help(self, ctx):
        """Mostrar ayuda"""
        embed = discord.Embed(
            title="📖 Comandos de PolyLoco",
            color=discord.Color.blue(),
        )
        
        commands_list = [
            ("!balance", "Ver balance actual"),
            ("!positions", "Ver posiciones abiertas"),
            ("!status", "Ver estado de los bots"),
            ("!estrategia", "Ver estrategia de trading"),
            ("!help", "Mostrar esta ayuda"),
        ]
        
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        await ctx.send(embed=embed)


def main():
    """Iniciar bot de Discord"""
    bot = PolyLocoBot()
    bot.run(config.discord.token)


if __name__ == "__main__":
    main()
