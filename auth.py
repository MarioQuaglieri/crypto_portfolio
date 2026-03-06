from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
alg = "HS256"
token_exp_min = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=token_exp_min)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=alg)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[alg])
        return payload
    except JWTError:
        return None