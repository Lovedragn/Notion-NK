from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_community.utilities import SQLDatabase

import os
import jwt
import json

from chatbot import main

FRONTEND_ORIGINS = os.getenv("FRONTEND_ORIGINS", "*")

# ----- App -----
app = FastAPI()
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
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
    return {"email":"sujith.sappani@gmail.com"}

#----- request -------
@app.post("/chat")
async def cal(body : Request):
    res = await body.json()
    session_email = verification(" {{{{{{{{{{{{{{{{{{{test}}}}}}}}}}}}}}}}}}}")
    result = await main(res["user_input"] , session_email["email"])
    return result
