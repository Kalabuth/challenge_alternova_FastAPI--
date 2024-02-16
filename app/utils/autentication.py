import bcrypt
import jwt 
import os
from jwt import exceptions
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def check_password(input_password, hashed_password):
    hashed_bytes = bytes.fromhex(hashed_password[2:])
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_bytes)


def generate_access_token(user_id):
    access_token_payload = {
        'exp': datetime.utcnow() + timedelta(minutes=25),  
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    token_secret = os.environ.get("TOKEN_SECRET")
    access_token = jwt.encode(access_token_payload, os.environ.get("TOKEN_SECRET"), algorithm='HS256')
    return access_token


def generate_refresh_token(user_id):
    refresh_token_payload = {
        'exp': datetime.utcnow() + timedelta(days=30), 
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    refresh_token = jwt.encode(refresh_token_payload, os.environ.get("TOKEN_SECRET"), algorithm='HS256')
    return refresh_token    


def handle_authorization(token, output):
    try:
        if output:
            return jwt.decode(token, os.environ.get("TOKEN_SECRET"), algorithms=['HS256'])
        jwt.decode(token, os.environ.get("TOKEN_SECRET"), algorithms=['HS256'])
    except exceptions.DecodeError:
        return JSONResponse(content={"message": "Invalid Token"}, status_code=401)
    except  exceptions.ExpiredSignatureError:
        return JSONResponse(content={"message": "Token Expired"}, status_code=401)


