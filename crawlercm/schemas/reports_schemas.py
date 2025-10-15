"""
Schemas used for API communication and report data serialization.

These Pydantic models define the structure of data returned by
the scraping services. They represent reports for sales, production
orders, and pending materials.
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field


class SalesReportItem(BaseModel):
    """
    Represents a single sales report entry.

    This model contains detailed information about a sales order,
    including customer details, product data, financial values, and
    profitability indicators.
    """

    cliente: str = Field(..., description="Customer name.")
    negociacao: str = Field(..., description="Negotiation or deal identifier.")
    tipo_servico: str = Field(..., description="Type of service or sales operation.")

    emissao_pv: Optional[date] = Field(
        None, description="Sales order issue date (PV emission)."
    )

    pedido_cliente: str = Field(..., description="Customer's order number.")
    op: str = Field(..., description="Production order code (OP).")
    numero_projeto: str = Field(..., description="Project or job number.")
    codigo: str = Field(..., description="Product code.")
    produto: str = Field(..., description="Product description.")

    previsao: Optional[date] = Field(
        None, description="Expected delivery or completion date."
    )

    qtde_pendente: int = Field(..., description="Pending quantity.")
    estoque: int = Field(..., description="Current stock level.")

    valor_unitario: float = Field(..., description="Unit price of the item.")
    ipi: Optional[float] = Field(None, description="IPI tax percentage, if applicable.")
    valor_total: float = Field(..., description="Total value for the order line.")
    custo_estrutura: float = Field(..., description="Structure or production cost.")
    lucratividade_rs: float = Field(..., description="Profitability in BRL.")
    lucratividade_percentual: float = Field(
        ..., description="Profitability percentage."
    )

    condicao_pagamento: str = Field(..., description="Payment condition or terms.")


class PendingOrdersItem(BaseModel):
    """
    Represents a pending production order entry.

    This model describes an ongoing or delayed production order,
    including product, quantity, client, and schedule information.
    """

    op: str = Field(..., description="Production order number.")
    cliente: str = Field(..., description="Customer name.")
    codigo: str = Field(..., description="Product code.")
    produto: str = Field(..., description="Product description.")
    criacao: Optional[date] = Field(None, description="Order creation date.")
    prazo: Optional[date] = Field(None, description="Expected due or completion date.")
    quantidade: int = Field(..., description="Total quantity to produce.")
    peso: float = Field(..., description="Total weight of the production order.")
    etapa: str = Field(..., description="Current production stage.")


class PendingMaterialsItem(BaseModel):
    """
    Represents a pending materials report entry.

    This model describes a material requirement or shortage within
    a production process, including references to the related
    order, product, and expected dates.
    """

    criacao: Optional[date] = Field(None, description="Creation date of the record.")
    servico: str = Field(..., description="Service or department responsible.")
    codigo: str = Field(..., description="Material code.")
    material: str = Field(..., description="Material name or description.")
    op: str = Field(..., description="Related production order number.")
    produto: str = Field(..., description="Product related to the material.")
    sub_produto: str = Field(..., description="Subproduct or component, if applicable.")
    previsao_op: Optional[date] = Field(
        None, description="Expected date for the production order."
    )
    quantidade: float = Field(..., description="Total quantity required.")
    pendente: float = Field(
        ..., description="Pending quantity still not received or produced."
    )
    unidade: str = Field(..., description="Measurement unit (e.g., kg, pcs).")
    situacao: str = Field(..., description="Current situation or status.")
    previsao_mp: Optional[date] = Field(
        None, description="Expected date for material availability."
    )
