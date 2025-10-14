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
    
    emissao_pv: Optional[date] = None
    
    pedido_cliente: str
    op: str
    numero_projeto: str
    codigo: str
    produto: str
    
    previsao: Optional[date] = None
    
    qtde_pendente: int
    estoque: int
    
    valor_unitario: float
    ipi: Optional[float] = None
    valor_total: float
    custo_estrutura: float
    lucratividade_rs: float
    lucratividade_percentual: float
    
    condicao_pagamento: str


class PendingOrder(BaseModel):
    op: str
    cliente: str
    codigo: str
    produto: str
    criacao: Optional[date] = None
    prazo: Optional[date] = None
    quantidade: int
    peso: float
    etapa: str


class PendingMaterial(BaseModel):
    criacao: Optional[date] = None
    servico: str
    codigo: str
    material: str
    op: str
    produto: str
    sub_produto: str
    previsao_op: Optional[date] = None
    quantidade: float
    pendente: float
    unidade: str
    situacao: str
    previsao_mp: Optional[date] = None