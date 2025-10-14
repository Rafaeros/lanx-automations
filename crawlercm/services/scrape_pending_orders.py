
import aiohttp
from bs4 import BeautifulSoup
from typing import List


from schemas.pending_order import ReportScraped

async def scrape_pending_orders(client: aiohttp.ClientSession, url: str, init_date: str, end_date: str) -> List[ReportScraped]:
    """
    Usa um cliente aiohttp já autenticado para fazer o scraping.
    """

    def _parse_float(value: str) -> float:
        """
        Converte uma string para float de forma inteligente, identificando
        automaticamente os separadores de milhar e decimal.
        Lida com formatos como '1.234,56' (BR) e '1,234.56' (US).
        """
        if not value or not isinstance(value, str) or not value.strip():
            return 0.0

        cleaned_value = value.strip()
        
        # Verifica a presença de ambos os separadores
        has_dot = '.' in cleaned_value
        has_comma = ',' in cleaned_value

        if has_dot and has_comma:
            # Se a vírgula vem depois do ponto, asumimos o formato BR (1.234,56)
            if cleaned_value.rfind(',') > cleaned_value.rfind('.'):
                # Remove os pontos (milhar) e substitui a vírgula (decimal) por ponto
                cleaned_value = cleaned_value.replace('.', '').replace(',', '.')
            else: # Senão, asumimos o formato US (1,234.56)
                # Remove as vírgulas (milhar)
                cleaned_value = cleaned_value.replace(',', '')
        elif has_comma:
            # Se há apenas vírgulas, elas podem ser de milhar ou um único decimal
            # Se for só uma vírgula e tiver 2 casas depois, é provável que seja decimal
            if cleaned_value.count(',') == 1 and len(cleaned_value.split(',')[1]) in [1, 2, 3]:
                cleaned_value = cleaned_value.replace(',', '.')
            else: # Mais de uma vírgula, são de milhar
                cleaned_value = cleaned_value.replace(',', '')

        # Se há apenas pontos, podem ser de milhar ou um único decimal
        # Se houver mais de um ponto, eles SÃO de milhar.
        elif cleaned_value.count('.') > 1:
            cleaned_value = cleaned_value.replace('.', '')
            
        try:
            return float(cleaned_value)
        except (ValueError, TypeError):
            return 0.0

    def _parse_int(value: str) -> int:
        """
        Converte uma string para int. Usa a inteligência da `parse_float`
        para lidar com diferentes formatos de número.
        Não precisa de alterações.
        """
        float_value = _parse_float(value)
        return int(float_value)
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        print("DATAS DO PARAMETRO: ", init_date, end_date)
        params = {
            'RelatorioPedidosPendentes[dataInicio]': f'{init_date}',
            'RelatorioPedidosPendentes[dataFim]': f'{end_date}',
            'RelatorioPedidosPendentes[considerarForecast]': '0',
            'RelatorioPedidosPendentes[emissor]': '37299632',
            'RelatorioPedidosPendentes[situacao]': '',
        }

        async with client.get(url, headers=headers, params=params, timeout=10.0) as response:
            response.raise_for_status()
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find("table", {"id": "tableExpo"})
            trs = table.find_all("tr")
            items_found: List[ReportScraped] = []
            for row in trs:
                if not row.text.strip():
                    break
                cells = row.find_all('td')

                if len(cells) >= 14:
                    item = ReportScraped(
                        cliente=cells[0].text.strip(),
                        negociacao=cells[1].text.strip(), 
                        tipo_servico=cells[2].text.strip(),
                        pedido_cliente=cells[4].text.strip(),
                        op=cells[5].text.strip(),
                        numero_projeto=cells[6].text.strip(),
                        codigo=cells[7].text.strip(),
                        produto=cells[8].text.strip(),
                        condicao_pagamento=cells[18].text.strip(),

                        emissao_pv=cells[3].text.strip() or None,
                        previsao=cells[9].text.strip() or None,
                        
                        qtde_pendente=_parse_int(cells[10].text),
                        estoque=_parse_int(cells[11].text),
                        valor_unitario=_parse_float(cells[12].text),
                        ipi=_parse_float(cells[13].text),
                        valor_total=_parse_float(cells[14].text),
                        custo_estrutura=_parse_float(cells[15].text),
                        lucratividade_rs=_parse_float(cells[16].text),
                        lucratividade_percentual=_parse_float(cells[17].text)
                    )
                    items_found.append(item)
            print(f"Items encontrados: {len(items_found)}")
    except aiohttp.ClientError as exc:
        print(f"Ocorreu um erro na requisição de scraping: {exc}")
        return []

    return items_found