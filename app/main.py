from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database import init_db
from app.routers import vending
from app.seed_data import seed_products
from app.config import settings

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


app.include_router(vending.router, prefix="/api/v1", tags=["vending"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and seed data on startup"""
    await init_db()
    seed_products()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the AI-powered Soda Vending Machine!",
        "docs": "/docs",
        "endpoints": {
            "purchase": "POST /api/v1/purchase",
            "inventory": "GET /api/v1/inventory",
            "transactions": "GET /api/v1/transactions"
        }
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, reload=settings.api_reload) 