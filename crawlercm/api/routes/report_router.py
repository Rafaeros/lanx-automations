"""
Routes for retrieving reports data via scraping.

This module defines endpoints that trigger asynchronous scraping
processes to fetch sales, production, and material-related reports
from external systems. Each route manages its own date range defaults,
formatting, and exception handling.

Endpoints:
    - /pending_sales → Fetches sales report data.
    - /pending_orders → Fetches pending production orders.
    - /pending_materials → Fetches pending material items.
"""

import aiohttp
from typing import List, Optional
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request, HTTPException, Response

from api import deps
from schemas.reports_schemas import (
    FilteredSalesReportItem,
    PendingMaterialsItem,
    SalesReportItem,
    PendingOrdersItem,
)
from services.scrape_reports import (
    get_combined_report_data,
    scrape_pending_materials,
    scrape_prod_pending_orders,
    scrape_sales_pending_orders,
)
from core.utils.format_excel import format_data_for_excel
from core.logger import logger
from core.config import settings

router = APIRouter()
init_date_str = (date.today() - timedelta(days=15)).strftime("%d/%m/%Y")
end_date_str = (date.today() + timedelta(days=90)).strftime("%d/%m/%Y")


@router.get("/pending_sales", response_model=List[SalesReportItem])
async def get_sales_pending_orders(
    client: aiohttp.ClientSession = Depends(deps.get_authenticated_client),
    init_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[SalesReportItem]:
    """
    Fetches sales orders via scraping.

    This endpoint triggers an asynchronous scraping process to retrieve
    sales orders from the external system. If no date range is provided,
    it defaults to the last 15 days and the next 30 days. Dates are internally
    formatted as DD/MM/YYYY before being sent to the target system.

    Args:
        client (aiohttp.ClientSession): An authenticated HTTP client injected via dependency.
        init_date (Optional[date], optional): Start date for the search range. Defaults to 15 days ago.
        end_date (Optional[date], optional): End date for the search range. Defaults to 30 days from today.

    Returns:
        List[SalesReportItem]: A list of sales orders retrieved from the external system.

    Raises:
        HTTPException: If any error occurs during the scraping process.
    """
    try:
        if init_date is None:
            init_date = init_date_str
        else:
            init_date = init_date.strftime("%d/%m/%Y")

        if end_date is None:
            end_date = end_date_str
        else:
            end_date = end_date.strftime("%d/%m/%Y")

        logger.info("Fetching sales pending orders...")
        report_data = await scrape_sales_pending_orders(
            client, settings.SALES_PENDING_ORDER_URL, init_date_str, end_date_str
        )
        if not report_data:
            raise HTTPException(
                status_code=404, detail="No sales pending orders found."
            )
        logger.info("Sales pending orders fetched successfully!")
        return report_data
    except Exception as e:
        logger.error(f"Error fetching sales pending orders: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching sales pending orders: {e}")


@router.get("/pending_orders", response_model=List[PendingOrdersItem])
async def get_prod_pending_orders(
    request: Request,
    client: aiohttp.ClientSession = Depends(deps.get_authenticated_client),
    init_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[PendingOrdersItem]:
    """
    Fetches pending production orders via scraping.

    This endpoint triggers an asynchronous scraping process to retrieve
    pending production orders from the external system. If no date range
    is provided, it defaults to the last 15 days and the next 30 days.

    Dates are internally formatted as DD/MM/YYYY before sending to the
    target system. The CSRF token required for authentication is accessed
    via the FastAPI app state.

    Args:
        request (Request): The FastAPI request object. Used to access app state data (e.g., CSRF token).
        client (aiohttp.ClientSession): An authenticated HTTP client injected via dependency.
        init_date (Optional[date], optional): Start date for the search range. Defaults to 15 days ago.
        end_date (Optional[date], optional): End date for the search range. Defaults to 30 days from today.

    Returns:
        List[PendingOrdersItem]: A list of pending production orders retrieved from the external system.

    Raises:
        HTTPException: If any error occurs during the scraping process.
    """

    try:
        if init_date is None:
            init_date = init_date_str
        else:
            init_date = init_date.strftime("%d/%m/%Y")

        if end_date is None:
            end_date = end_date_str
        else:
            end_date = end_date.strftime("%d/%m/%Y")

        logger.info("Fetching production pending orders...")
        csrf_token = request.app.state.csrf_token
        report_data = await scrape_prod_pending_orders(
            client,
            settings.PROD_PENDING_ORDER_URL,
            init_date_str,
            end_date_str,
            csrf_token,
        )

        if not report_data:
            raise HTTPException(
                status_code=404, detail="No production pending orders found."
            )

        logger.info("Production pending orders fetched successfully!")
        return report_data
    except Exception as e:
        logger.error(f"Error fetching production pending orders: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching production pending orders: {e}")


@router.get("/pending_materials", response_model=List[PendingMaterialsItem])
async def get_pending_materials(
    client: aiohttp.ClientSession = Depends(deps.get_authenticated_client),
) -> List[PendingMaterialsItem]:
    """
    Fetches pending material items via scraping.

    This endpoint triggers an asynchronous scraping process to retrieve
    pending materials data from the external system. It requires a
    previously authenticated client session.

    Args:
        client (aiohttp.ClientSession): An authenticated HTTP client injected via dependency.

    Returns:
        List[PendingMaterialsItem]: A list of pending materials retrieved from the external system.

    Raises:
        HTTPException: If any error occurs during the scraping process.
    """
    try:
        logger.info("Fetching pending materials...")
        report_data = await scrape_pending_materials(
            client, settings.PENDING_MATERIALS_URL
        )

        if not report_data:
            raise HTTPException(status_code=404, detail="No pending materials found.")

        logger.info("Pending materials fetched successfully!")
        return report_data
    except Exception as e:
        logger.error(f"Error fetching pending materials: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching pending materials: {e}")


@router.get("/filtered_sales_report", response_model=List[FilteredSalesReportItem])
async def get_filtered_sales_report(
    request: Request,
    client: aiohttp.ClientSession = Depends(deps.get_authenticated_client), 
    init_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[FilteredSalesReportItem]:
    """
    Fetches pending sales, orders and  material items via scraping.

    This endpoint triggers an asynchronous scraping process to retrieve
    pending materials data from the external system. It requires a
    previously authenticated client session.

    Args:
        request (Request): The FastAPI request object. Used to access app state data (e.g., CSRF token).
        client (aiohttp.ClientSession): An authenticated HTTP client injected via dependency.
        init_date (Optional[date], optional): Start date for the search range. Defaults to 15 days ago.
        end_date (Optional[date], optional): End date for the search range. Defaults to 30 days from today.
        
    Returns:
        List[FilteredSalesReportItem]: A list of pending sales, orders and  material items retrieved from the external system.

    Raises:
        HTTPException: If any error occurs during the scraping process.
    """
    try:
        if init_date is None:
            init_date = init_date_str
        else:
            init_date = init_date.strftime("%d/%m/%Y")

        if end_date is None:
            end_date = end_date_str
        else:
            end_date = end_date.strftime("%d/%m/%Y")

        logger.info("Fetching combining sales reports...")
        urls = {
            "sales": settings.SALES_PENDING_ORDER_URL,
            "prod": settings.PROD_PENDING_ORDER_URL,
            "materials": settings.PENDING_MATERIALS_URL
        }
        csrf_token = request.app.state.csrf_token

        report_data = await get_combined_report_data(
            client, urls, init_date, end_date, csrf_token
        )
        logger.info("Sales filtered report fetched successfully!")
        return report_data
    except Exception as e:
        logger.error(f"Error fetching sales filtered report: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching sales filtered report: {e}")
    
@router.get("/filtered_sales_report/export", tags=["Consolidated Reports"])
async def export_filtered_sales_report(
    request: Request,
    client: aiohttp.ClientSession = Depends(deps.get_authenticated_client),
    init_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """
    Fetches sales, order, and pending material data and exports it to an Excel file.

    This endpoint triggers an asynchronous scraping process to consolidate data
    and generates an .xlsx file for download. It requires a previously 
    authenticated client session.

    Args:
        request (Request): The FastAPI request object.
        client (aiohttp.ClientSession): An authenticated HTTP client injected via dependency.
        init_date (Optional[date]): The start date for the filter. Defaults to 15 days ago.
        end_date (Optional[date]): The end date for the filter. Defaults to 30 days from today.
        
    Returns:
        Response: A FastAPI Response object containing the generated Excel file for download.

    Raises:
        HTTPException: If an error occurs during the scraping or file generation process.
    """
    if init_date is None:
        init_date = init_date_str
    else:
        init_date = init_date.strftime("%d/%m/%Y")

    if end_date is None:
        end_date = end_date_str
    else:
        end_date = end_date.strftime("%d/%m/%Y")
    
    try:
        urls = {
            "sales": settings.SALES_PENDING_ORDER_URL,
            "prod": settings.PROD_PENDING_ORDER_URL,
            "materials": settings.PENDING_MATERIALS_URL,
        }
        csrf_token = request.app.state.csrf_token
        
        report_data = await get_combined_report_data(
            client, urls, init_date_str, end_date_str, csrf_token
        )
        logger.info("Getting excel bytes for filtered sales report...")
        excel_bytes = format_data_for_excel(report_data)
        file_name = f"relatorio_carteira_{date.today().strftime('%Y-%m-%d')}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        headers = {
            'Content-Disposition': f'attachment; filename="{file_name}"'
        }
        logger.info("Excel file generated successfully!")
        return Response(
            content=excel_bytes,
            media_type=media_type,
            headers=headers
        )
    except Exception as e:
        logger.error(f"Error exporting filtered sales report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export report: {e}")
