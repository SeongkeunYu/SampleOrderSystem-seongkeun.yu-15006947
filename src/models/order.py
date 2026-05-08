from dataclasses import dataclass
from enum import Enum


class OrderStatus(Enum):
    RESERVED = "RESERVED"
    REJECTED = "REJECTED"
    PRODUCING = "PRODUCING"
    CONFIRMED = "CONFIRMED"
    RELEASE = "RELEASE"


@dataclass
class Order:
    id: str
    sample_id: str
    customer_name: str
    quantity: int
    status: OrderStatus
    created_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sample_id": self.sample_id,
            "customer_name": self.customer_name,
            "quantity": self.quantity,
            "status": self.status.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Order":
        return cls(
            id=d["id"],
            sample_id=d["sample_id"],
            customer_name=d["customer_name"],
            quantity=d["quantity"],
            status=OrderStatus(d["status"]),
            created_at=d["created_at"],
        )
