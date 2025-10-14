import aiohttp
from typing import List, Optional

from fastapi import APIRouter
from fastapi import Depends
from datetime import datetime as dt
from datetime import timedelta

from api import deps
from schemas.pending_order import ReportScraped
from services.scrape_pending_orders import scrape_pending_orders
from core.config import settings

router = APIRouter()


@router.get("/pedidos_pendentes", response_model=List[ReportScraped])
async def trigger_scraping(
    client: aiohttp.ClientSession = Depends(deps.get_authenticated_client),
    init_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Dispara o processo de scraping e retorna os itens encontrados.
    """
    if init_date is None:
        init_date = (dt.now() - timedelta(days=15)).strftime('%d/%m/%Y')
    if end_date is None:
        end_date = (dt.now() + timedelta(days=30)).strftime('%d/%m/%Y')

    report_data = await scrape_pending_orders(client, settings.PENDING_ORDER_URL, init_date, end_date)

    return report_data
