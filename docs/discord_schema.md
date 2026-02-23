# Schema de Discord - PolyLoco Trading Server

## 🏗️ Estructura de Canales

### 📊 CATEGORÍA: TRADING

#### Canales de Texto:

| Canal | ID | Descripción | Uso |
|-------|-----|-------------|-----|
| `#💰balance` | PENDIENTE | Balance y portfolio | Alertas de saldo, fondeo |
| `#📈trades` | PENDIENTE | Trades ejecutados | Cada trade con detalles |
| `#📉posiciones` | PENDIENTE | Posiciones abiertas | Estado de posiciones |
| `#⚠️alertas` | PENDIENTE | Alertas importantes | Errores, oportunidades |
| `#📊estadisticas` | PENDIENTE | Reportes diarios | PnL, win rate, etc. |

#### Canales de Voz:
- `🔊 Trading Floor` - Para discusiones en vivo (opcional)

---

### 🤖 CATEGORÍA: BOTS

| Canal | ID | Descripción |
|-------|-----|-------------|
| `#🐦elon-tweets` | PENDIENTE | Bot de Elon Tweets |
| `#⚡fast-loop` | PENDIENTE | Bot de Fast Loop (BTC) |
| `#🎯mert-sniper` | PENDIENTE | Bot de Mert Sniper |
| `#📡signal-sniper` | PENDIENTE | Bot de Signal Sniper |
| `#🌡️weather` | PENDIENTE | Bot de Weather Trader |

---

### 📚 CATEGORÍA: ESTRATEGIAS

| Canal | ID | Descripción |
|-------|-----|-------------|
| `#📖estrategias` | PENDIENTE | Discusión de estrategias |
| `#💡ideas` | PENDIENTE | Nuevas ideas de trading |
| `#📊backtesting` | PENDIENTE | Resultados de backtests |
| `#🔧configuracion` | PENDIENTE | Ajustes de bots |

---

### 🎛️ CATEGORÍA: ADMIN

| Canal | ID | Descripción |
|-------|-----|-------------|
| `#🔒logs` | PENDIENTE | Logs del sistema (privado) |
| `#⚙️config` | PENDIENTE | Configuración (privado) |

---

## 🎯 Estrategias por Bot

### 🐦 Elon Tweet Trader
- **Canal**: `#🐦elon-tweets`
- **Estrategia**: Comprar buckets adyacentes cuando costo < $1
- **Frecuencia**: Cada 2 minutos
- **Monto**: $1 por trade
- **Diversificación**: Máx 1 posición Elon

### ⚡ Fast Loop
- **Canal**: `#⚡fast-loop`
- **Estrategia**: Momentum BTC de Binance > 0.5%
- **Frecuencia**: Cada 1 minuto
- **Monto**: $1 por trade
- **Mercados**: BTC 5min/15min

### 🎯 Mert Sniper
- **Canal**: `#🎯mert-sniper`
- **Estrategia**: Mercados expirando con split 60/40
- **Frecuencia**: Cada 2 minutos
- **Monto**: $1 por trade

### 📡 Signal Sniper
- **Canal**: `#📡signal-sniper`
- **Estrategia**: Noticias RSS con keywords
- **Frecuencia**: Cada 5 minutos
- **Monto**: $1 por trade

### 🌡️ Weather Trader
- **Canal**: `#🌡️weather`
- **Estrategia**: NOAA forecasts vs mercados de temperatura
- **Frecuencia**: Cada 2 minutos
- **Monto**: $1 por trade

---

## 📋 Configuración de Variables

### Para cada canal, necesito:

```bash
# Canales principales
DISCORD_CHANNEL_BALANCE=ID
DISCORD_CHANNEL_TRADES=ID
DISCORD_CHANNEL_POSITIONS=ID
DISCORD_CHANNEL_ALERTS=ID
DISCORD_CHANNEL_STATS=ID

# Canales de bots
DISCORD_CHANNEL_ELON=ID
DISCORD_CHANNEL_FAST=ID
DISCORD_CHANNEL_MERT=ID
DISCORD_CHANNEL_SIGNAL=ID
DISCORD_CHANNEL_WEATHER=ID
```

---

## 🚀 Próximos Pasos

1. **Crear canales en Discord** con los nombres de arriba
2. **Copiar los IDs** de cada canal
3. **Configurar variables** en Railway
4. **Actualizar código** para usar canales específicos por bot

**¿Creás los canales y me pasás los IDs?**
