from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import report_routes
from core.session_manager import lifespan

origins = [
    "http://localhost",
    "http://localhost:8090",
    "*"
]

app = FastAPI(title="API de Scraping", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(report_routes.router, prefix="/api", tags=["Scraping"])

@app.get("/")
def read_root():
    return {"status": "API online"}