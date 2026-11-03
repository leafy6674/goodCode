from collections import defaultdict
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import now
from ..database import get_db
from ..models import Order, Role, User
from ..schemas import (
    MonthlyHoursOut,
    MonthlyRevenue,
    RegisterIn,
    StaffHoursRow,
    SummaryOut,
    UserOut,
)
from ..security import hash_password, require_roles
from .attendance import monthly_report, open_shift

router = APIRouter(
    prefix="/api/manager",
    tags=["manager"],
    dependencies=[Depends(require_roles(Role.manager))],
)


@router.get("/summary", response_model=SummaryOut)
def summary(
    start: date | None = None,
    end: date | None = None,
    db: Session = Depends(get_db),
):
    """營運資料：營收、訂單數、客單價、熱銷商品、每日營收、時段分佈。"""
    today = now().date()
    end = end or today
    start = start or end - timedelta(days=29)
    if start > end:
        raise HTTPException(400, "開始日期不可晚於結束日期")
    lo = datetime.combine(start, datetime.min.time())
    hi = datetime.combine(end + timedelta(days=1), datetime.min.time())

    orders = db.scalars(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.created_at >= lo, Order.created_at < hi, Order.status == "completed")
    ).all()

    revenue = sum(o.total for o in orders)
    product: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    daily: dict[str, list[int]] = {}
    d = start
    while d <= end:
        daily[d.isoformat()] = [0, 0]
        d += timedelta(days=1)
    hourly = [0] * 24
    cups = 0
    for o in orders:
        key = o.created_at.date().isoformat()
        daily[key][0] += 1
        daily[key][1] += o.total
        hourly[o.created_at.hour] += 1
        for it in o.items:
            product[it.product_name][0] += it.quantity
            product[it.product_name][1] += it.quantity * it.unit_price
            cups += it.quantity

    top = sorted(product.items(), key=lambda kv: kv[1][1], reverse=True)[:10]
    return SummaryOut(
        start=start.isoformat(),
        end=end.isoformat(),
        order_count=len(orders),
        revenue=revenue,
        avg_order_value=round(revenue / len(orders), 1) if orders else 0,
        cups_sold=cups,
        member_orders=sum(1 for o in orders if o.customer_id is not None),
        top_products=[
            {"product_name": k, "quantity": v[0], "revenue": v[1]} for k, v in top
        ],
        daily=[{"date": k, "orders": v[0], "revenue": v[1]} for k, v in daily.items()],
        hourly=[{"hour": h, "orders": c} for h, c in enumerate(hourly)],
    )


@router.get("/monthly-revenue", response_model=list[MonthlyRevenue])
def monthly_revenue(months: int = Query(12, ge=1, le=36), db: Session = Depends(get_db)):
    """近 N 個月每月營收。"""
    t = now()
    y, m = t.year, t.month
    keys = []
    for _ in range(months):
        keys.append(f"{y:04d}-{m:02d}")
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    keys.reverse()
    first = datetime(int(keys[0][:4]), int(keys[0][5:]), 1)
    rows = db.execute(
        select(Order.created_at, Order.total).where(
            Order.created_at >= first, Order.status == "completed"
        )
    ).all()
    found = {k: [0, 0] for k in keys}
    for created_at, total in rows:
        k = created_at.strftime("%Y-%m")
        if k in found:
            found[k][0] += 1
            found[k][1] += total
    return [{"month": k, "orders": v[0], "revenue": v[1]} for k, v in found.items()]


@router.get("/staff-hours", response_model=list[StaffHoursRow])
def staff_hours(
    year: int | None = Query(None, ge=2000, le=2100),
    month: int | None = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
):
    """所有店員當月工時與目前打卡狀態。"""
    t = now()
    year, month = year or t.year, month or t.month
    staff = db.scalars(
        select(User).where(User.role.in_([Role.staff.value, Role.manager.value]))
    ).all()
    rows = []
    for s in staff:
        rep = monthly_report(db, s.id, year, month)
        rows.append(
            StaffHoursRow(
                staff_id=s.id,
                name=s.name,
                username=s.username,
                total_hours=rep.total_hours,
                shifts=rep.shifts,
                days_worked=rep.days_worked,
                on_duty=open_shift(db, s.id) is not None,
            )
        )
    return rows


@router.get("/staff/{staff_id}/monthly", response_model=MonthlyHoursOut)
def staff_monthly(
    staff_id: int,
    year: int | None = Query(None, ge=2000, le=2100),
    month: int | None = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
):
    if db.get(User, staff_id) is None:
        raise HTTPException(404, "找不到店員")
    t = now()
    return monthly_report(db, staff_id, year or t.year, month or t.month)


@router.post("/staff", response_model=UserOut, status_code=201)
def create_staff(body: RegisterIn, db: Session = Depends(get_db)):
    """店長新增店員帳號。"""
    if db.scalar(select(User).where(User.username == body.username)):
        raise HTTPException(400, "此帳號已存在")
    u = User(
        username=body.username,
        password_hash=hash_password(body.password),
        name=body.name,
        phone=body.phone,
        role=Role.staff.value,
    )
    db.add(u)
    db.commit()
    return u
