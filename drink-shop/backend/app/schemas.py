from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)
    name: str = Field(min_length=1, max_length=50)
    phone: str | None = Field(default=None, max_length=20)


class LoginIn(BaseModel):
    username: str
    password: str


class UserOut(ORM):
    id: int
    username: str
    name: str
    phone: str | None
    role: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ProductOut(ORM):
    id: int
    name: str
    category: str
    price: int


class OrderItemIn(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=50)
    sugar: str = "正常糖"
    ice: str = "正常冰"


class OrderIn(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1)


class OrderItemOut(ORM):
    product_name: str
    unit_price: int
    quantity: int
    sugar: str
    ice: str


class OrderOut(ORM):
    id: int
    created_at: datetime
    total: int
    status: str
    items: list[OrderItemOut]


class MyOrdersOut(BaseModel):
    since: datetime
    until: datetime
    count: int
    total_spent: int
    orders: list[OrderOut]


class AttendanceOut(ORM):
    id: int
    clock_in: datetime
    clock_out: datetime | None
    hours: float | None


class ClockStatusOut(BaseModel):
    on_duty: bool
    current: AttendanceOut | None
    today_hours: float


class MonthlyHoursOut(BaseModel):
    year: int
    month: int
    total_hours: float
    shifts: int
    days_worked: int
    records: list[AttendanceOut]


class StaffHoursRow(BaseModel):
    staff_id: int
    name: str
    username: str
    total_hours: float
    shifts: int
    days_worked: int
    on_duty: bool


class ProductSales(BaseModel):
    product_name: str
    quantity: int
    revenue: int


class DailyRevenue(BaseModel):
    date: str
    orders: int
    revenue: int


class SummaryOut(BaseModel):
    start: str
    end: str
    order_count: int
    revenue: int
    avg_order_value: float
    cups_sold: int
    member_orders: int
    top_products: list[ProductSales]
    daily: list[DailyRevenue]
    hourly: list[dict]


class MonthlyRevenue(BaseModel):
    month: str
    orders: int
    revenue: int
