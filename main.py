import logger
import logging

logger = logging.getLogger(__name__)

from api import get_crypto_data
from analytics import prepare_dataframe, calculate_portfolio_value, calculate_weight
from plotting import plot, plot_history
from storage import save_portfolio_history
import time
from config import portfolio, refresh_seconds

def main():
    logger.info("Avvio programma...")

    raw_data = get_crypto_data(portfolio)
    logger.info("Dati API ricevuti")

    df = prepare_dataframe(raw_data, portfolio)
    df = calculate_weight(df)

    total_value = calculate_portfolio_value(df)
    logger.info(f"Valore totale portafoglio: ${total_value:,.2f}")

    save_portfolio_history(total_value)
    logger.info("Storico salvato")

    plot(df)
    plot_history()
    return df


if __name__ == "__main__":
    try:
        while True:
            main()
            logger.info(f"Prossimo aggiornamento tra {refresh_seconds} secondi")
            time.sleep(refresh_seconds)
    except KeyboardInterrupt as e:
        logger.info(f"Programma interrotto dall'utente")
