import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.ai import router as ai_router

load_dotenv()

app = FastAPI()

# CORS configuration
frontend_origins = os.getenv("FRONTEND_ORIGINS", "*")
allow_origins = [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]
app.add_middleware(
	CORSMiddleware,
	allow_origins=allow_origins if allow_origins else ["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Routers
app.include_router(ai_router)
