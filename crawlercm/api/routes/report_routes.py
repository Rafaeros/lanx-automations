import aiohttp
from typing import List, Optional
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request, HTTPException

from api import deps 
from schemas.reports_schemas import PendingMaterial, ReportScraped, PendingOrder
from services.scrape_reports import scrape_pending_materials, scrape_prod_pending_orders, scrape_sales_pending_orders
from core.config import settings


router = APIRouter()

@router.get("/pedidos_pendentes_vendas", response_model=List[ReportScraped])
async def get_sales_pending_orders(
    client: aiohttp.ClientSession = Depends(deps.get_authenticated_client),
    init_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """
    Dispara o processo de scraping e retorna os itens encontrados.
    As datas devem ser enviadas no formato AAAA-MM-DD.
    """
    if init_date is None:
        init_date = date.today() - timedelta(days=15)
    if end_date is None:
        end_date = date.today() + timedelta(days=30)
    
    init_date_str = init_date.strftime('%d/%m/%Y')
    end_date_str = end_date.strftime('%d/%m/%Y')

    try:
        report_data = await scrape_sales_pending_orders(
            client,
            settings.SALES_PENDING_ORDER_URL,
            init_date_str,
            end_date_str
        )
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro no scraping: {e}")


@router.get("/ordens_pendentes", response_model=List[PendingOrder])
async def get_prod_pending_orders(
    request: Request,
    client: aiohttp.ClientSession = Depends(deps.get_authenticated_client),
    init_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """
    Dispara o processo de scraping e retorna os itens encontrados.
    """

    if init_date is None:
        init_date = date.today() - timedelta(days=15)
    if end_date is None:
        end_date = date.today() + timedelta(days=30)
    
    init_date_str = init_date.strftime('%d/%m/%Y')
    end_date_str = end_date.strftime('%d/%m/%Y')
    try:
        csrf_token = request.app.state.csrf_token
        report_data = await scrape_prod_pending_orders(
            client,
            settings.PROD_PENDING_ORDER_URL,
            init_date_str,
            end_date_str,
            csrf_token
        )
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro no scraping: {e}")
    

@router.get("/materiais_em_falta", response_model=List[PendingMaterial])
async def get_pending_materials(
    client: aiohttp.ClientSession = Depends(deps.get_authenticated_client)
):
    """
    Dispara o processo de scraping e retorna os itens encontrados.
    """
    try:
        report_data = await scrape_pending_materials(client, settings.PENDING_MATERIALS_URL)
        return report_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro no scraping: {e}")