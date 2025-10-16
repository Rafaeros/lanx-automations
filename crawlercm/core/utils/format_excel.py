from io import BytesIO
from typing import List

import pandas as pd
from schemas.reports_schemas import FilteredSalesReportItem

def format_data_for_excel(report_data: List[FilteredSalesReportItem]) -> bytes:
    """
    Converte a lista de dados consolidados em um DataFrame do Pandas,
    formatando colunas complexas para melhor visualização no Excel.
    """
    if not report_data:
        return pd.DataFrame()

    header_mapping = {
        "negociacao": "Negociação",
        "pedido_cliente": "Pedido do Cliente",
        "op": "Ordem de Produção (OP)",
        "tipo_servico": "Tipo de Serviço",
        "numero_projeto": "Nº do Projeto",
        "codigo": "Código do Produto",
        "produto": "Descrição do Produto",
        "previsao": "Previsão de Entrega",
        "qtde_pendente": "Qtde. Pendente",
        "valor_unitario": "Valor Unitário (R$)",
        "ipi": "IPI (%)",
        "valor_total": "Valor Total (R$)",
        "etapa": "Etapa Atual",
        "materiais_pendentes": "Materiais Pendentes"
    }

    dados_para_df = [item.model_dump() for item in report_data]
    for item in dados_para_df:
        materiais_str_list = []
        for mat in item.get('materiais_pendentes', []):
            code = mat.get('codigo', 'N/A')
            pendente = mat.get('pendente', 'N/A')
            situacao = mat.get('situacao', 'N/A')
            previsao_mp = mat.get('previsao_mp', 'N/A')
            if previsao_mp != 'N/A' and hasattr(previsao_mp, 'strftime'):
                formated_date = previsao_mp.strftime('%d/%m/%Y')
            else:
                formated_date = 'N/A'
            materiais_str_list.append(f"Cod.: {code} | Qtde. Pendente: {pendente} | STATUS: {situacao} | PREV: {formated_date}")
        item['materiais_pendentes'] = "; \n".join(materiais_str_list) if materiais_str_list else ""
    df = pd.DataFrame(dados_para_df)
    df.rename(columns=header_mapping, inplace=True)
    
    if "Previsão de Entrega" in df.columns:
        df["Previsão de Entrega"] = pd.to_datetime(df["Previsão de Entrega"])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter', datetime_format='dd/mm/yyyy') as writer:
        df.to_excel(writer, sheet_name='RelatorioVendas', index=False)

        workbook = writer.book
        worksheet = writer.sheets['RelatorioVendas']

        currency_format = workbook.add_format({'num_format': 'R$ #,##0.00'})
        integer_format = workbook.add_format({'num_format': '0'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy', 'align': 'left'})
        text_wrap_format = workbook.add_format({'text_wrap': True, 'valign': 'top'})

        col_map = {col: i for i, col in enumerate(df.columns)}

        if "Valor Unitário (R$)" in col_map:
            worksheet.set_column(col_map["Valor Unitário (R$)"], col_map["Valor Unitário (R$)"], None, currency_format)
        if "Valor Total (R$)" in col_map:
            worksheet.set_column(col_map["Valor Total (R$)"], col_map["Valor Total (R$)"], None, currency_format)
        if "Qtde. Pendente" in col_map:
            worksheet.set_column(col_map["Qtde. Pendente"], col_map["Qtde. Pendente"], None, integer_format)
        if "Previsão de Entrega" in col_map:
            worksheet.set_column(col_map["Previsão de Entrega"], col_map["Previsão de Entrega"], 12, date_format)
            
        for i, col in enumerate(df.columns):
            column_len = df[col].astype(str).map(len).max()
            header_len = len(col)
            max_len = max(column_len, header_len) + 2
            
            if max_len > 60:
                if col == "Materiais Pendentes":
                    worksheet.set_column(i, i, 50, text_wrap_format)
                else:
                    worksheet.set_column(i, i, 60)
            else:
                worksheet.set_column(i, i, max_len)

    return output.getvalue()