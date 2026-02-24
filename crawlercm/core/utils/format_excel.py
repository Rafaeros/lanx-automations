from io import BytesIO
from typing import List

import pandas as pd
from schemas.reports_schemas import FilteredSalesReportItem

def format_data_for_excel(report_data: List[FilteredSalesReportItem]) -> bytes:
    """
    Converte a lista de dados consolidados em um DataFrame do Pandas,
    formatando com cores alternadas, bordas restritas aos dados e 
    alinhamentos personalizados.
    """
    header_mapping = {
        "negociacao": "Negociação",
        "pedido_cliente": "Pedido do Cliente",
        "op": "Ordem",
        "tipo_servico": "Tipo de Serviço",
        "cliente": "Cliente",
        "codigo": "Código",
        "produto": "Descrição",
        "previsao": "Previsão",
        "qtde_pendente": "Pendente",
        "valor_total": "Valor Total (R$)",
        "etapa": "Etapa Atual",
        "materiais_pendentes": "Materiais Pendentes"
    }

    if not report_data:
        df = pd.DataFrame(columns=list(header_mapping.values()))
    else:
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
        
        if "Previsão" in df.columns:
            df["Previsão"] = pd.to_datetime(df["Previsão"], errors='ignore')

    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter', datetime_format='dd/mm/yyyy') as writer:
        if df.empty:
            df.to_excel(writer, sheet_name='RelatorioVendas', index=False)
            return output.getvalue()

        workbook = writer.book
        worksheet = workbook.add_worksheet('RelatorioVendas')
        header_format = workbook.add_format({
            'bg_color': '#4472C4',
            'font_color': '#FFFFFF',
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        for col_num, col_name in enumerate(df.columns):
            worksheet.write(0, col_num, col_name, header_format)

        formats = {}
        for col in df.columns:
            for is_even in (True, False):
                bg_color = '#D9E1F2' if is_even else '#FFFFFF'
                if col in ["Cliente", "Materiais Pendentes", "Descrição"]:
                    align = 'left'
                else:
                    align = 'center'
                
                fmt_dict = {
                    'bg_color': bg_color,
                    'border': 1,
                    'align': align,
                    'valign': 'vcenter'
                }
                
                if col == "Materiais Pendentes":
                    fmt_dict['text_wrap'] = True
                elif col in ["Valor Unitário (R$)", "Valor Total (R$)"]:
                    fmt_dict['num_format'] = 'R$ #,##0.00'
                elif col == "Pendente":
                    fmt_dict['num_format'] = '0'
                elif col in ["Previsão", "Previsão de Entrega"]:
                    fmt_dict['num_format'] = 'dd/mm/yyyy'

                formats[(col, is_even)] = workbook.add_format(fmt_dict)

        for row_num, row_data in enumerate(df.itertuples(index=False)):
            is_even_row = (row_num % 2 == 0)
            
            for col_num, cell_value in enumerate(row_data):
                col_name = df.columns[col_num]
                cell_fmt = formats[(col_name, is_even_row)]
                
                if pd.isna(cell_value):
                    worksheet.write_blank(row_num + 1, col_num, "", cell_fmt)
                elif col_name in ["Previsão", "Previsão de Entrega"] and isinstance(cell_value, pd.Timestamp):
                    worksheet.write_datetime(row_num + 1, col_num, cell_value.to_pydatetime(), cell_fmt)
                else:
                    worksheet.write(row_num + 1, col_num, cell_value, cell_fmt)

        max_row = len(df)
        max_col = len(df.columns)
        worksheet.autofilter(0, 0, max_row, max_col - 1)
        for i, col in enumerate(df.columns):
            if col == "Materiais Pendentes":
                max_data_len = df[col].dropna().astype(str).apply(
                    lambda x: max([len(line) for line in x.split('\n')]) if x else 0
                ).max()
            else:
                max_data_len = df[col].astype(str).map(len).max()

            if pd.isna(max_data_len): 
                max_data_len = 0
                
            header_len = len(col)
            max_len = max(max_data_len, header_len) + 4
            width = min(max_len, 55 if col == "Materiais Pendentes" else 60)
            worksheet.set_column(i, i, width)

    return output.getvalue()