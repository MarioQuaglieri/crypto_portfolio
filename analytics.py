import pandas as pd
import logging
logger = logging.getLogger(__name__)

def prepare_dataframe(df, portfolio):
    try:
        df = df[["id", "name", "current_price", "price_change_percentage_24h"]]
        df["quantity"] = df["id"].map(portfolio)
        df["total_value"] = df["current_price"] * df["quantity"]
        logger.info(f"Dataframe preparato con {len(df)} asset")
        return df
    except KeyError as e:
        logger.error(f"Colonna mancante nel dataframe: {e}")
        raise
    except Exception as e:
        logger.error(f"Error nella preparazione del dataframe: {e}")
        raise

def calculate_portfolio_value(df):
    try:
        total =  df["total_value"].sum()
        logger.info("Valore totale calcolato")
        return total
    except Exception as e:
        logger.error(f"Error nel calcolare il valore totale: {e}")
        raise

def calculate_weight(df):
    try:
        total = df["total_value"].sum()
        df["weight_%"] = (df["total_value"] / total) * 100
        logger.info("Pesi calcolati correttamente")
        return df
    except ZeroDivisionError:
        logger.error("Impossibile calcolare i pesi: valore totale è zero")
        raise
    except Exception as e:
        logger.error(f"Errore nel calcolo dei pesi: {e}")
        raise