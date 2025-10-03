import os
import jwt
import json

from fastapi import FastAPI, Request , HTTPException , status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_community.utilities import SQLDatabase

from chatbot import main

FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173")

# ----- App -----
app = FastAPI()

allowed_origins = [o.strip().rstrip('/') for o in FRONTEND_ORIGINS.split(',') if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -------- SQL --------

import urllib.parse

password = urllib.parse.quote_plus("Sujith@6212")
DB_URL = f"mysql+mysqlconnector://root:{password}@localhost:3306/knot"

db = SQLDatabase.from_uri(DB_URL)
print("Connected!")


def verification(token : str):
    
    # secret = "sujith-namekart"
    # issuer = "knot"
    #
    # # Encode a token
    # token = jwt.encode(
    #     {"some": "payload", "iss": issuer},
    #     secret,
    #     algorithm="HS256"
    # )
    # print("Token:", token)
    return "sujith.sappani@gmail.com"

############# request ############
@app.post("/chat")
async def cal(body : Request):
    res = await body.json()
    auth: str | None = body.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized Access")

    session_email = verification(auth)
    result =await main(res["user_input"] , session_email)
    return result["answer"]
