"""
Service to scrape reports data from CM.

This module contains functions that use an authenticated aiohttp client session
to scrape various reports (sales pending orders, production pending orders,
and pending materials) from the CM system. Helper functions are included to
parse numeric and date strings from the HTML tables.
"""

from datetime import date, datetime
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Optional

from core.logger import logger
from schemas.reports_schemas import (
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

    if ',' in cleaned_value:
        cleaned_value = cleaned_value.replace('.', '').replace(',', '.')
    
    elif '.' in cleaned_value:
        parts = cleaned_value.split('.')
        if len(parts[-1]) == 3 and len(parts) > 1:
            cleaned_value = ''.join(parts)
        else:
            cleaned_value = ''.join(parts[:-1]) + '.' + parts[-1]

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
            url, headers=headers, params=params, timeout=30.0
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
            logger.info(f"Items found: {len(items_found)}")
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
            url, headers=headers, params=params, timeout=30.0
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
            print(f"Items found: {len(items_found)}")
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
            url, headers=headers, params=params, timeout=30.0
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
    except aiohttp.ClientError as e:
        logger.error(f"Error scraping pending materials: {e}")
        return []

    return items_found
