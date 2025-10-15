"""
Main module for the API.

This module defines the FastAPI app and its routes.
It also includes middleware for handling CORS and logging.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import report_router
from core.session_manager import lifespan

origins = ["http://localhost", "http://localhost:8090", "*"]
app = FastAPI(title="API de Scraping", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(report_router.router, prefix="/api", tags=["Scraping"])


@app.on_event("startup")
async def startup_event():
    """
    Startup event for the API.
    """
    from core.logger import logger
    logger.info("Initializing API")
    logger.info("Configuring CORS and API Routes")


@app.get("/")
def read_root():
    """
    Root endpoint for the API.

    Returns:
        dict: A dictionary containing the status of the API.
    """
    return {"status": "API online"}
