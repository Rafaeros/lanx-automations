from fastapi import FastAPI
from api.routes import pending_orders
from core.session_manager import lifespan

app = FastAPI(title="API de Scraping", lifespan=lifespan)
app.include_router(pending_orders.router, prefix="/api", tags=["Scraping"])

@app.get("/")
def read_root():
    return {"status": "API online"}