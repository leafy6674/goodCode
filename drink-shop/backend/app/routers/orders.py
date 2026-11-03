from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import months_ago, now
from ..database import get_db
from ..models import Order, OrderItem, Product, Role, User
from ..schemas import MyOrdersOut, OrderIn, OrderOut, ProductOut
from ..security import get_current_user, require_roles

router = APIRouter(prefix="/api", tags=["orders"])

SUGAR_OPTIONS = ["正常糖", "少糖", "半糖", "微糖", "無糖"]
ICE_OPTIONS = ["正常冰", "少冰", "微冰", "去冰", "溫", "熱"]


@router.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.scalars(
        select(Product).where(Product.is_active).order_by(Product.category, Product.id)
    ).all()


@router.get("/options")
def options():
    return {"sugar": SUGAR_OPTIONS, "ice": ICE_OPTIONS}


@router.post("/orders", response_model=OrderOut, status_code=201)
def create_order(
    body: OrderIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.customer)),
):
    order = Order(customer_id=user.id, created_at=now())
    total = 0
    for item in body.items:
        product = db.get(Product, item.product_id)
        if product is None or not product.is_active:
            raise HTTPException(400, f"商品 {item.product_id} 不存在")
        if item.sugar not in SUGAR_OPTIONS or item.ice not in ICE_OPTIONS:
            raise HTTPException(400, "甜度或冰塊選項錯誤")
        order.items.append(
            OrderItem(
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=item.quantity,
                sugar=item.sugar,
                ice=item.ice,
            )
        )
        total += product.price * item.quantity
    order.total = total
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders/me", response_model=MyOrdersOut)
def my_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """客戶會員查詢自己 12 個月之內的所有訂單。"""
    until = now()
    since = months_ago(until, 12)
    orders = db.scalars(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.customer_id == user.id, Order.created_at >= since)
        .order_by(Order.created_at.desc())
    ).all()
    return MyOrdersOut(
        since=since,
        until=until,
        count=len(orders),
        total_spent=sum(o.total for o in orders),
        orders=[OrderOut.model_validate(o) for o in orders],
    )
