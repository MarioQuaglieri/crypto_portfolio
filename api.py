import requests
import pandas as pd
import logging
logger = logging.getLogger(__name__)

def get_crypto_data(portfolio):
    logger.info("Chiamata API in corso...")
    url = "https://api.coingecko.com/api/v3/coins/markets"
    
    params = {
        "vs_currency": "usd",
        "ids": ",".join(portfolio.keys()),
        "order": "market_cap_desc",
        "per_page": len(portfolio),
        "page": 1,
        "price_change_percentage": "24h"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        logger.info(f"Dati ricevuti correttamente ({len(response.json())} asset)")
        return pd.DataFrame(response.json())
    
    except requests.exceptions.ConnectionError:
        logger.error("Impossibile connettersi all'API, controlla la connessione")
        raise
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"Errore HTTP: {e}")
        raise
    
    except Exception as e:
        logger.error(f"Errore inaspettato: {e}")
        raise