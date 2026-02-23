"""
Notificador de Discord usando Webhook
Más simple que bot, no requiere invitación
"""
import requests
import json
from datetime import datetime
from typing import Dict, Any


class DiscordWebhook:
    """Enviar notificaciones a Discord via webhook"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_message(self, content: str, embeds: list = None) -> bool:
        """Enviar mensaje simple"""
        data = {"content": content}
        if embeds:
            data["embeds"] = embeds
        
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code == 204
        except Exception as e:
            print(f"Error enviando webhook: {e}")
            return False
    
    def send_trade_notification(
        self,
        bot_name: str,
        market: str,
        side: str,
        amount: float,
        success: bool,
        profit: float = None
    ) -> bool:
        """Notificación de trade"""
        color = 0x00ff00 if success else 0xff0000
        
        embed = {
            "title": f"🤖 {bot_name}",
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {"name": "Mercado", "value": market[:100], "inline": False},
                {"name": "Side", "value": side.upper(), "inline": True},
                {"name": "Monto", "value": f"${amount:.2f}", "inline": True},
                {"name": "Estado", "value": "✅ Éxito" if success else "❌ Fallido", "inline": True},
            ]
        }
        
        if profit is not None:
            embed["fields"].append(
                {"name": "Profit", "value": f"${profit:.2f}", "inline": True}
            )
        
        return self.send_message("", [embed])
    
    def send_balance_alert(self, balance: float, exposure: float) -> bool:
        """Alerta de balance"""
        available = balance - exposure
        color = 0x00ff00 if available > 0 else 0xff0000
        
        embed = {
            "title": "💰 Balance Actual",
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {"name": "USDC Total", "value": f"${balance:.2f}", "inline": True},
                {"name": "Exposure", "value": f"${exposure:.2f}", "inline": True},
                {"name": "Disponible", "value": f"${available:.2f}", "inline": True},
            ]
        }
        
        return self.send_message("", [embed])
    
    def send_startup_message(self) -> bool:
        """Mensaje de inicio"""
        embed = {
            "title": "🚀 PolyLoco Trading Bot",
            "description": "Sistema de trading activado",
            "color": 0x3498db,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {"name": "Estado", "value": "🟢 Online", "inline": True},
                {"name": "Bots", "value": "Elon, Fast, Mert, Signal", "inline": True},
            ]
        }
        return self.send_message("", [embed])


def main():
    """Probar webhook"""
    import os
    
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL no configurado")
        return
    
    webhook = DiscordWebhook(webhook_url)
    
    # Enviar mensaje de prueba
    print("Enviando mensaje de prueba...")
    if webhook.send_startup_message():
        print("✅ Mensaje enviado")
    else:
        print("❌ Error enviando mensaje")


if __name__ == "__main__":
    main()
