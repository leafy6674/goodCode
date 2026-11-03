from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .config import now
from .database import Base


class Role(str, Enum):
    customer = "customer"  # 客戶會員
    staff = "staff"  # 店員
    manager = "manager"  # 店長


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str | None] = mapped_column(String(20), default=None)
    role: Mapped[str] = mapped_column(String(20), default=Role.customer.value)
    created_at: Mapped[datetime] = mapped_column(default=now)

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer", foreign_keys="Order.customer_id"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(30))
    price: Mapped[int]  # NT$, integer
    is_active: Mapped[bool] = mapped_column(default=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(default=now, index=True)
    total: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(20), default="completed")

    customer: Mapped[User | None] = relationship(
        back_populates="orders", foreign_keys=[customer_id]
    )
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product_name: Mapped[str] = mapped_column(String(50))  # snapshot at order time
    unit_price: Mapped[int]
    quantity: Mapped[int]
    sugar: Mapped[str] = mapped_column(String(20), default="正常糖")
    ice: Mapped[str] = mapped_column(String(20), default="正常冰")

    order: Mapped[Order] = relationship(back_populates="items")


class Attendance(Base):
    """One shift: clock in -> clock out."""

    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    clock_in: Mapped[datetime] = mapped_column(index=True)
    clock_out: Mapped[datetime | None] = mapped_column(default=None)

    staff: Mapped[User] = relationship()

    @property
    def hours(self) -> float | None:
        if self.clock_out is None:
            return None
        return round((self.clock_out - self.clock_in).total_seconds() / 3600, 2)
