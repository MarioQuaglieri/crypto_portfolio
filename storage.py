import pandas as pd
from datetime import datetime
import logging
import mysql.connector
from mysql.connector import cursor

logger = logging.getLogger(__name__)

def save_portfolio_history(total_value):
    try:
        connection = mysql.connector.connect(
            host="localhsot",
            user="root",
            password="",
            database="crypto_db"
        )

        cursor = connection.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO report (Data_Log, Valore_Portfolio) VALUES (%s, %s)"
        values =(now, total_value)

        cursor.execute(sql, values)
        connection.commit()
        logger.info(f"Storico salvato nel Database")
    except mysql.connector.Error as e:
        logger.error(f"Errore database: {e}")
        raise
    finally:
        cursor.close()
        connection.close()
        logger.info("Connessione al database chiusa")