# PolyLoco - Velocity Trader

⚡ **Estrategia de Alta Velocidad para Polymarket**

Bot automatizado enfocado exclusivamente en **Fast Loop 5-15 minutos** para BTC, ETH y SOL.

## 🎯 Estrategia

### Concepto
Ser más rápido que Polymarket. El bot detecta movimientos de precio en Binance **5-15ms antes** de que Polymarket reaccione, y entra primero.

```
Real price move:     t = 0ms
Bot reaction:        t = +5-10ms  ← NOSOTROS AQUÍ
Polymarket reaction: t = +20-35ms
```

### Ventana Exploitable
**Δt ≈ 5-15ms** de ventaja para entrar antes que el mercado.

## ⚡ Características

- **Assets**: BTC, ETH, SOL simultáneos
- **Timeframe**: 5-15 minutos
- **Scan**: Cada 5 segundos
- **Divergencia mínima**: 0.5%
- **Monto por trade**: $2
- **Fees**: 10% (fast markets)

## 📊 Resultados Esperados

Basado en traders que usan esta estrategia:
- **100+ trades/día**
- **$20,000+ diarios** (con capital suficiente)
- **ROI**: 90%+ mensual

## 🚀 Setup

1. **Clonar repo**
2. **Configurar variables** en `.env`:
   ```
   SIMMER_API_KEY=...
   WALLET_PRIVATE_KEY=...
   ```
3. **Deploy en Railway**
4. **Fondear** Polymarket con $50+

## 💰 Capital Recomendado

- **Mínimo**: $20
- **Óptimo**: $50-100
- **Distribución**: 100% Velocity Trader

## 🛠️ Tecnología

- **Python 3.11+**
- **Simmer SDK**: Trading en Polymarket
- **Binance API**: Precios en tiempo real
- **Railway**: Hosting 24/7

## ⚠️ Disclaimer

Trading de alta frecuencia conlleva riesgos. Los resultados pasados no garantizan resultados futuros.

---

**Estrategia basada en**: [@0x_Discover](https://x.com/0x_Discover)
