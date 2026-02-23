"""
Bot de Discord para PolyLoco
"""
import asyncio
import discord
from discord.ext import commands, tasks
from datetime import datetime
from src.config.settings import config
from src.trading.simmer_client import SimmerTrader


class PolyLocoBot(commands.Bot):
    """Bot de Discord para monitorear y controlar trading"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )
        
        self.trader = SimmerTrader()
        self.channel_id = config.discord.channel_id
    
    async def setup_hook(self):
        """Setup inicial"""
        self.monitor_trades.start()
    
    async def on_ready(self):
        """Bot listo"""
        print(f"✅ {self.user} conectado")
        channel = self.get_channel(self.channel_id)
        if channel:
            await channel.send("🚀 **PolyLoco Bot activado**\nMonitoreando trades...")
    
    @tasks.loop(minutes=2)
    async def monitor_trades(self):
        """Monitorear trades cada 2 minutos"""
        channel = self.get_channel(self.channel_id)
        if not channel:
            return
        
        # Verificar balance
        portfolio = self.trader.get_portfolio()
        balance = portfolio.get("balance_usdc", 0)
        exposure = portfolio.get("total_exposure", 0)
        available = balance - exposure
        
        # Solo alertar si hay cambios significativos
        if available < 0:
            await channel.send(
                f"⚠️ **Balance bajo**\n"
                f"Disponible: ${available:.2f}\n"
                f"Fondear para continuar trading"
            )
    
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
            ("Elon Tweet Trader", "🐦", "Cada 2 min"),
            ("Fast Loop", "⚡", "Cada 1 min"),
            ("Mert Sniper", "🎯", "Cada 2 min"),
            ("Signal Sniper", "📡", "Cada 5 min"),
        ]
        
        for name, emoji, freq in bots:
            embed.add_field(
                name=f"{emoji} {name}",
                value=f"Frecuencia: {freq}\nEstado: 🟢 Activo",
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
