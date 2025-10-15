"""
Service to scrape reports data from CM.

This module contains functions that use an authenticated aiohttp client session
to scrape various reports (sales pending orders, production pending orders,
and pending materials) from the CM system. Helper functions are included to
parse numeric and date strings from the HTML tables.
"""

import asyncio
from collections import defaultdict
from datetime import date, datetime
from io import BytesIO
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Optional
import pandas as pd

from core.logger import logger
from schemas.reports_schemas import (
    FilteredSalesReportItem,
    PendingMaterialsItem,
    SalesReportItem,
    PendingOrdersItem,
)


def _parse_float(value: str) -> float:
    """
    Converte uma string para float, lidando com formatos brasileiros (ex: "1.300,00")
    e aplicando uma heurística para valores ambíguos como "1.300".

    Args:
        value (str): A string numérica a ser convertida.

    Returns:
        float: O valor float convertido. Retorna 0.0 se a conversão falhar.
    """
    if not isinstance(value, str):
        return 0.0

    cleaned_value = value.strip()
    if not cleaned_value:
        return 0.0

    if "," in cleaned_value:
        cleaned_value = cleaned_value.replace(".", "").replace(",", ".")

    elif "." in cleaned_value:
        parts = cleaned_value.split(".")
        if len(parts[-1]) == 3 and len(parts) > 1:
            cleaned_value = "".join(parts)
        else:
            cleaned_value = "".join(parts[:-1]) + "." + parts[-1]

    try:
        return float(cleaned_value)
    except (ValueError, TypeError):
        return 0.0


def _parse_int(value: str) -> int:
    """
    Parse a string into an integer using `_parse_float`.

    Args:
        value (str): Numeric string.

    Returns:
        int: Parsed integer value.
    """
    float_value = _parse_float(value)
    return int(float_value)


def _parse_date(date_str: str) -> Optional[date]:
    """
    Parse a short date string into a date object.

    Args:
        date_str (str): Date string in format "DD/MM/YY".

    Returns:
        Optional[date]: Date object, or None if parsing fails.
    """
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str, "%d/%m/%y").date()
    except ValueError:
        return None


async def scrape_sales_pending_orders(
    client: aiohttp.ClientSession, url: str, init_date: str, end_date: str
) -> List[SalesReportItem]:
    """
    Scrape the sales pending orders report from the CM system.

    Args:
        client (aiohttp.ClientSession): Authenticated aiohttp client session.
        url (str): URL of the sales pending orders report.
        init_date (str): Start date in "DD/MM/YYYY" format.
        end_date (str): End date in "DD/MM/YYYY" format.

    Returns:
        List[SalesReportItem]: List of parsed sales report items.

    Raises:
        aiohttp.ClientError: If the HTTP request fails.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        params = {
            "RelatorioPedidosPendentes[dataInicio]": f"{init_date}",
            "RelatorioPedidosPendentes[dataFim]": f"{end_date}",
            "RelatorioPedidosPendentes[considerarForecast]": "0",
            "RelatorioPedidosPendentes[emissor]": "37299632",
            "RelatorioPedidosPendentes[situacao]": "",
        }
        logger.info("Scraping sales pending orders...")
        async with client.get(
            url, headers=headers, params=params
        ) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table", {"id": "tableExpo"})
            trs = table.find_all("tr")[1:]
            items_found: List[SalesReportItem] = []

            for tr in trs:
                if not tr.text.strip():
                    break

                tds = tr.find_all("td")
                if len(tds) >= 14:
                    item = SalesReportItem(
                        cliente=tds[0].text.strip(),
                        negociacao=tds[1].text.strip(),
                        tipo_servico=tds[2].text.strip(),
                        pedido_cliente=tds[4].text.strip(),
                        op=tds[5].text.strip(),
                        numero_projeto=tds[6].text.strip(),
                        codigo=tds[7].text.strip(),
                        produto=tds[8].text.strip(),
                        condicao_pagamento=tds[18].text.strip(),
                        emissao_pv=tds[3].text.strip() or None,
                        previsao=tds[9].text.strip() or None,
                        qtde_pendente=_parse_int(tds[10].text),
                        estoque=_parse_int(tds[11].text),
                        valor_unitario=_parse_float(tds[12].text),
                        ipi=_parse_float(tds[13].text),
                        valor_total=_parse_float(tds[14].text),
                        custo_estrutura=_parse_float(tds[15].text),
                        lucratividade_rs=_parse_float(tds[16].text),
                        lucratividade_percentual=_parse_float(tds[17].text),
                    )
                    items_found.append(item)
            logger.info(f"Pendind Sales Items found: {len(items_found)}")
    except aiohttp.ClientError as e:
        logger.error(f"Error scraping sales pending orders: {e}")
        return []

    return items_found


async def scrape_prod_pending_orders(
    client: aiohttp.ClientSession,
    url: str,
    init_date: str,
    end_date: str,
    yii_token: str,
) -> List[PendingOrdersItem]:
    """
    Scrape the production pending orders report from the CM system.

    Args:
        client (aiohttp.ClientSession): Authenticated aiohttp client session.
        url (str): URL of the production pending orders report.
        init_date (str): Start date in "DD/MM/YYYY" format.
        end_date (str): End date in "DD/MM/YYYY" format.
        yii_token (str): CSRF token required for POST requests.

    Returns:
        List[PendingOrdersItem]: List of parsed production pending orders.

    Raises:
        aiohttp.ClientError: If the HTTP request fails.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        params = {
            "dataInicio": init_date,
            "dataFim": end_date,
            "clienteId": "",
            "YII_CSRF_TOKEN": yii_token,
        }
        logger.info("Scraping production pending orders...")
        async with client.post(
            url, headers=headers, params=params
        ) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table", {"id": "tableExpo"})
            trs = table.find_all("tr")[1:]
            items_found: List[PendingOrdersItem] = []
            for tr in trs:
                tds = tr.find_all("td")
                if tds:
                    item = PendingOrdersItem(
                        op=tds[0].text.strip(),
                        cliente=tds[1].text.strip(),
                        codigo=tds[2].text.strip(),
                        produto=tds[3].text.strip(),
                        criacao=_parse_date(tds[4].text.strip()),
                        prazo=_parse_date(tds[5].text.strip()),
                        quantidade=_parse_int(tds[6].text.strip()),
                        peso=_parse_float(tds[7].text.strip()),
                        etapa=tds[8].text.strip(),
                    )
                    items_found.append(item)
            logger.info(f"Pending Orders Items found: {len(items_found)}")
    except aiohttp.ClientError as e:
        logger.error(f"Error scraping production pending orders: {e}")
        return []

    return items_found


async def scrape_pending_materials(
    client: aiohttp.ClientSession,
    url: str,
) -> List[PendingMaterialsItem]:
    """
    Scrape the pending materials report from the CM system.

    Args:
        client (aiohttp.ClientSession): Authenticated aiohttp client session.
        url (str): URL of the pending materials report.

    Returns:
        List[PendingMaterialsItem]: List of parsed pending materials items.

    Raises:
        aiohttp.ClientError: If the HTTP request fails.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        params = {
            "Pedido[_nomeMaterial]": "",
            "Pedido[_solicitante]": "",
            "Pedido[status_id]": "",
            "Pedido[situacao]": "TODAS",
            "Pedido[_qtdeFornecida]": "Parcialmente",
            "Pedido[_inicioCriacao]": "01/01/2025",
            "Pedido[_fimCriacao]": "",
            "pageSize": "20",
        }
        logger.info("Scraping pending materials")
        async with client.get(
            url, headers=headers, params=params
        ) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table", {"id": "tableExpo"})
            trs = table.find_all("tr")[1:]
            items_found: List[PendingMaterialsItem] = []
            for tr in trs:
                tds = tr.find_all("td")
                if tds:
                    item = PendingMaterialsItem(
                        criacao=_parse_date(tds[0].text.strip()),
                        servico=tds[1].text.strip(),
                        codigo=tds[2].text.strip(),
                        material=tds[3].text.strip(),
                        op=tds[4].text.strip(),
                        produto=tds[5].text.strip(),
                        sub_produto=tds[6].text.strip(),
                        previsao_op=_parse_date(tds[7].text.strip()),
                        quantidade=_parse_float(tds[8].text.strip().split(" ")[0]),
                        pendente=_parse_float(tds[9].text.strip().split(" ")[0]),
                        unidade=tds[9].text.strip().split(" ")[-1],
                        situacao=tds[10].text.strip(),
                        previsao_mp=_parse_date(tds[11].text.strip()),
                    )
                    items_found.append(item)
            logger.info(f"Pending Materials Items found: {len(items_found)}")
    except aiohttp.ClientError as e:
        logger.error(f"Error scraping pending materials: {e}")
        return []

    return items_found


def combine_data(
    sales_reports: List[SalesReportItem],
    pending_orders: List[PendingOrdersItem],
    pending_materials: List[PendingMaterialsItem],
) -> List[FilteredSalesReportItem]:
    """
    Combine the data of sales reports, production pending orders, and pending materials, by op number value.

    Args:
        sales_reports (List[SalesReportItem]): List of sales report items.
        pending_orders (List[PendingOrdersItem]): List of production pending orders.
        pending_materials (List[PendingMaterialsItem]): List of pending materials.

    Returns:
        List[FilteredSalesReportItem]: List of parsed production pending orders.
    """
    try:
        logger.info("Combining data...")
        orders_map = {order.op: order for order in pending_orders}
        materials_map = defaultdict(list)
        for material in pending_materials:
            materials_map[material.op].append(material)

        filtered_sales_list = []
        for sales_item in sales_reports:
            current_op = sales_item.op
            matching_order = orders_map.get(current_op)
            etapa_producao = matching_order.etapa if matching_order else "N/A"
            matching_materials = materials_map.get(current_op, [])

            filtered_item = FilteredSalesReportItem(
                negociacao=sales_item.negociacao,
                pedido_cliente=sales_item.pedido_cliente,
                op=sales_item.op,
                tipo_servico=sales_item.tipo_servico,
                numero_projeto=sales_item.numero_projeto,
                codigo=sales_item.codigo,
                produto=sales_item.produto,
                previsao=sales_item.previsao,
                qtde_pendente=sales_item.qtde_pendente,
                valor_unitario=sales_item.valor_unitario,
                ipi=sales_item.ipi,
                valor_total=sales_item.valor_total,
                etapa=etapa_producao,
                materiais_pendentes=matching_materials,
            )
            filtered_sales_list.append(filtered_item)
    except Exception as e:
        logger.error(f"Error combining data: {e}")
        return []

    return filtered_sales_list


async def get_combined_report_data(
    client: aiohttp.ClientSession,
    urls: dict[str, str],
    init_date_str: str,
    end_date_str: str,
    csrf_token: str,
) -> List[FilteredSalesReportItem]:
    """
    Scrape the production pending orders report from the CM system.

    Args:
        client (aiohttp.ClientSession): Authenticated aiohttp client session.
        urls (dict[str]): URLs for different report sources.
        init_date (str): Start date in "DD/MM/YYYY" format.
        end_date (str): End date in "DD/MM/YYYY" format.
        yii_token (str): CSRF token required for POST requests.

    Returns:
        List[FilteredSalesReportItem]: List of parsed production pending orders.

    Raises:
        aiohttp.ClientError: If the HTTP request fails.
    """
    try:
        logger.info("Starting parallel tasks for scraping of all report sources...")
        
        tasks = [
            scrape_sales_pending_orders(client, urls["sales"], init_date_str, end_date_str),
            scrape_prod_pending_orders(client, urls["prod"], init_date_str, end_date_str, csrf_token),
            scrape_pending_materials(client, urls["materials"]),
        ]
        
        sales_data, orders_data, materials_data = await asyncio.gather(*tasks, return_exceptions=True)

        for result in [sales_data, orders_data, materials_data]:
            if isinstance(result, Exception):
                logger.error(f"A scraping task failed: {result}")
                raise result

        logger.info("All scraping tasks completed successfully. Combining data...")
        
        combined_list = combine_data(sales_data, orders_data, materials_data)
        
        logger.info("Data combined successfully!")
    except Exception as e:
        logger.error(f"Error combining data: {e}")

    return combined_list