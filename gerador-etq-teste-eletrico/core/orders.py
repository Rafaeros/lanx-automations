import json
from dataclasses import dataclass
from datetime import datetime as dt
from typing import List, Dict

from core.utils.path_utils import resource_path

ORDER_PATH = "tmp/reports/"


@dataclass
class Order:
    deliver_date: dt.date
    code: int
    product: str
    description: str
    quantity: int

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            deliver_date=dt.strptime(data["deliver_date"], "%Y-%m-%d %H:%M:%S"),
            code=int(data["code"]),
            product=data["product"],
            description=data["description"],
            quantity=int(data["quantity"]),
        )

    def to_dict(self):
        return {
            "deliver_date": self.deliver_date.strftime("%Y-%m-%d %H:%M:%S"),
            "code": self.code,
            "product": self.product,
            "description": self.description,
            "quantity": self.quantity,
        }


class OrderList:
    def __init__(self):
        self.orders: List[Order] = []

    def create_order(
        self,
        deliver_date: dt.date,
        code: int,
        product: str,
        description: str,
        quantity: int,
    ) -> Order:
        order = Order(
            deliver_date=deliver_date,
            code=code,
            product=product,
            description=description,
            quantity=quantity,
        )
        self.orders.append(order)
        return order

    def to_dict(self) -> Dict[str, dict]:
        return {str(o.code): o.to_dict() for o in self.orders}

    def to_json(self):
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=4)


class OrderManager:
    def __init__(self):
        super().__init__()


    def get_order_by_code(self, code: int) -> Order | None:
        now = dt.now().strftime("%d-%m-%Y")
        file_path = resource_path(f"{ORDER_PATH}{now}_orders.json")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        order_data = data.get(str(code))
        if not order_data:
            return None

        return Order.from_dict(order_data)
