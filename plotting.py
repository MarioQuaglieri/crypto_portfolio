import plotly.express as px
import pandas as pd
import mysql.connector
import logging
logger = logging.getLogger(__name__)

def plot(df):
    fig_pie = px.pie(
        df, 
        names=df["name"],
        values=df["total_value"], 
        title="Distribuzione del portafoglio per valore",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hover_data=["current_price", "quantity"]
    )

    fig_bar = px.bar(
        df,
        x="name", 
        y="price_change_percentage_24h",
        title="Variazione % nelle ultime 24 ore",
        text="price_change_percentage_24h",
        color="price_change_percentage_24h",
        color_continuous_scale=px.colors.sequential.Oranges
        )
    fig_bar.update_layout(yaxis_title="% Change")

    fig_pie.show()
    fig_bar.show()

def plot_history():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="crypto_db"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT Data_Log, Valore_Portfolio FROM report ORDER BY Data_Log ASC")
        rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=["Data_Log", "Valore_Portfolio"])
        fig_line = px.line(df, x="Data_Log", y="Valore_Portfolio", title="Andamento Portfolio")
        fig_line.show()
    except mysql.connector.Error as e:
        logger.error(f"Errore database: {e}")
    finally:
        cursor.close()
        connection.close()