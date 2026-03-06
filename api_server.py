from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import mysql.connector
from analytics import prepare_dataframe, calculate_portfolio_value, calculate_weight
from config import portfolio
from api import get_crypto_data
from pydantic import BaseModel
import json
from dotenv import load_dotenv
import os
from auth import hash_password, verify_password, create_token, verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
load_dotenv()

class UserInput(BaseModel):
    username: str
    password: str

class CoinInput(BaseModel):
    coin: str
    quantity: float

class QuantityInput(BaseModel):
    quantity: float

app = FastAPI()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token non valido o scaduto")
    return payload["sub"]

@app.get("/")
def home():
    return {"messaggio": "server funzionante"}

@app.get("/history")
def get_history(current_user: str = Depends(get_current_user)):
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
def get_portfolio(current_user: str = Depends(get_current_user)):
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
def get_coin(coin: str, current_user: str = Depends(get_current_user)):
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
def add_coin(data: CoinInput, current_user: str = Depends(get_current_user)):
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
def del_coin(coin: str, current_user: str = Depends(get_current_user)):
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
def put_coin(coin: str, data: QuantityInput, current_user: str = Depends(get_current_user)):
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
def patch_coin(coin: str, data: QuantityInput, current_user: str = Depends(get_current_user)):
    if not coin in portfolio:
        raise HTTPException(status_code=404, detail=f"{coin} non è presente nel portfolio")
    
    portfolio[coin] += data.quantity

    with open("config.json", "r") as file:
        config = json.load(file)

    config["portfolio"][coin] += data.quantity

    with open("config.json", "w") as file:
        json.dump(config, file, indent=4)

    return {"messaggio": f"{coin} aggiunta correttamente al portfolio con nuova quantità {portfolio[coin]}"}


@app.post("/signin", status_code=201)
def sign_in(data: UserInput):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM users WHERE username = %s", (data.username,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Username già esistente")
    
    hashed = hash_password(data.password)
    cursor.execute("INSERT INTO users (username, hashed_password) VALUES (%s, %s)", (data.username, hashed))
    connection.commit()
    cursor.close()
    connection.close()

    return {"messaggio": f"Utente {data.username} registrato correttamente"}

@app.post("/login")
def login(data: OAuth2PasswordRequestForm = Depends()):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT hashed_password FROM users WHERE username = %s", (data.username,))
    
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user or not verify_password(data.password, user[0]):
        raise HTTPException(status_code=401, detail="Credenziali non valide")
    
    token = create_token({"sub": data.username})
    return {"access_token": token, "token_type": "bearer"}