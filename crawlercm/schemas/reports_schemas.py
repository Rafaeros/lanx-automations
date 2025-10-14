from typing import Optional
from datetime import date
from pydantic import BaseModel

class ReportScraped(BaseModel):
    """
    Schema para validar os dados extraídos do relatório.
    """
    cliente: str
    negociacao: str
    tipo_servico: str
    
    # Datas são opcionais, pois podem não estar sempre presentes
    emissao_pv: Optional[date] = None
    
    pedido_cliente: str
    op: str
    numero_projeto: str
    codigo: str
    produto: str
    
    previsao: Optional[date] = None
    
    qtde_pendente: int
    estoque: int
    
    # Para valores monetários, `float` é comum, mas `Decimal` é mais preciso.
    # Se a precisão for crítica, considere usar: from decimal import Decimal
    valor_unitario: float
    ipi: Optional[float] = None
    valor_total: float
    custo_estrutura: float
    lucratividade_rs: float
    lucratividade_percentual: float
    
    condicao_pagamento: str


class PendingOrder(BaseModel):
    """
    Schema para validar os dados extraídos do relatório.
    """
    op: str
    cliente: str
    codigo: str
    produto: str
    criacao: Optional[date] = None
    prazo: Optional[date] = None
    quantidade: int
    peso: float
    etapa: str