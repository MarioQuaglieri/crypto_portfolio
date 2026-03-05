import json
import logging
logger = logging.getLogger(__name__)

def load_config():
    try:
        with open("config.json", "r") as file:
            config = json.load(file)
            logger.info("Configurazione caricata correttamente")
            return config
    except FileNotFoundError as e:
        logger.info("File 'config.json' non è stato trovato")
        raise
    except json.JSONDecodeError as e:
        logger.info(f"Errore nel parsing del 'config.json': {e}")
        raise
    except Exception as e:
        logger.info(f"Errore non previsto: {e}")
        raise

config = load_config()
portfolio = config["portfolio"]
refresh_seconds = config["refresh_seconds"]