"""
Archivo principal - Entry point
"""
import sys
import argparse
from src.config.settings import config


def run_trading():
    """Ejecutar bots de trading"""
    print("🚀 Iniciando bots de trading...")
    # TODO: Importar y ejecutar bots
    pass


def run_discord():
    """Ejecutar bot de Discord"""
    print("🤖 Iniciando bot de Discord...")
    from src.discord.bot import main
    main()


def main():
    """Entry point principal"""
    parser = argparse.ArgumentParser(description="PolyLoco Trading Bot")
    parser.add_argument(
        "mode",
        choices=["trading", "discord", "all"],
        nargs="?",  # Hace el argumento opcional
        default="discord",  # Default a discord
        help="Modo de ejecución",
    )
    
    args = parser.parse_args()
    
    # Validar configuración
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        sys.exit(1)
    
    # Ejecutar según modo
    if args.mode == "trading":
        run_trading()
    elif args.mode == "discord":
        run_discord()
    elif args.mode == "all":
        # TODO: Ejecutar ambos en paralelo
        run_trading()


if __name__ == "__main__":
    main()
