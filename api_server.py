from fastapi import FastAPI, HTTPException
import mysql.connector
from analytics import prepare_dataframe, calculate_portfolio_value, calculate_weight
from config import portfolio
from api import get_crypto_data
from pydantic import BaseModel
import json

class CoinInput(BaseModel):
    coin: str
    quantity: float

class QuantityInput(BaseModel):
    quantity: float

app = FastAPI()

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="crypto_db"
    )


@app.get("/")
def home():
    return {"messaggio": "server funzionante"}

@app.get("/history")
def get_history():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT Data_Log, Valore_Portfolio FROM report ORDER BY Data_Log ASC")
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return [{"data": str(row[0]), "valore": row[1]} for row in rows]
    except mysql.connector.Error:
        raise HTTPException(status_code=503, detail="Database non raggiungibile")

@app.get("/portfolio")
def get_portfolio():
    try:
        raw_data = get_crypto_data(portfolio)
        df = prepare_dataframe(raw_data, portfolio)
        df = calculate_weight(df)
        total_value = calculate_portfolio_value(df)
        return {
            "total value": round(total_value, 2),
            "assets": df.to_dict(orient="records")
        }
    except Exception:
        raise HTTPException(status_code=503, detail="Errore nel recupero dei dati")

@app.get("/portfolio/{coin}")
def get_coin(coin: str):
    try:
        portfolio_coin = {coin: portfolio[coin]}
        raw_data = get_crypto_data(portfolio_coin)
        df = prepare_dataframe(raw_data, portfolio_coin)
        total_value = calculate_portfolio_value(df)

        return {
            "coin": coin,
            "current price": float(df["current_price"].values[0]),
            "quantity": portfolio[coin],
            "total value": float(round(total_value, 2))
        }
    
    except:
        raise HTTPException(status_code=404, detail=f"{coin} non è presente nel portfolio")
    

@app.post("/portfolio", status_code=201)
def add_coin(data: CoinInput):
    if data.coin in portfolio:
        raise HTTPException(status_code=400, detail=f"{data.coin} è già presente nel portfolio, usa PUT per modificare la quantità")
    
    portfolio[data.coin] = data.quantity

    with open("config.json", "r") as file:
        config = json.load(file)
    
    config["portfolio"][data.coin] = data.quantity
    
    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)
    
    return {"messaggio": f"{data.coin} aggiunto con quantità {data.quantity}"}


@app.delete("/portfolio/{coin}")
def del_coin(coin: str):
    if not coin in portfolio:
        raise HTTPException(status_code=404, detail=f"{coin} non è presente nel portfolio")
    
    del portfolio[coin]

    with open("config.json", "r") as file:
        config = json.load(file)

    del config["portfolio"][coin]

    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)
        
    return {"messaggio": f"{coin} correttamente eliminata dal portfolio"}


@app.put("/portfolio/{coin}")
def put_coin(coin: str, data: QuantityInput):
    if not coin in portfolio:
        raise HTTPException(status_code=404, detail=f"{coin} non è presente nel portfolio")
    
    portfolio[coin] = data.quantity

    with open("config.json", "r") as file:
        config = json.load(file)

    config["portfolio"][coin] = data.quantity

    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)

    return {"messaggio": f"{coin} aggiunta correttamente al portfolio con nuova quantità {portfolio[coin]}"}

@app.patch("/portfolio/{coin}")
def patch_coin(coin: str, data: QuantityInput):
    if not coin in portfolio:
        raise HTTPException(status_code=404, detail=f"{coin} non è presente nel portfolio")
    
    portfolio[coin] += data.quantity

    with open("config.json", "r") as file:
        config = json.load(file)

    config["portfolio"][coin] += data.quantity

    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)

    return {"messaggio": f"{coin} aggiunta correttamente al portfolio con nuova quantità {portfolio[coin]}"}