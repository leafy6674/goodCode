import calendar
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import now
from ..database import get_db
from ..models import Attendance, Role, User
from ..schemas import AttendanceOut, ClockStatusOut, MonthlyHoursOut
from ..security import require_roles

router = APIRouter(prefix="/api/attendance", tags=["attendance"])

staff_only = require_roles(Role.staff, Role.manager)


def month_range(year: int, month: int) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1)
    last = calendar.monthrange(year, month)[1]
    end = datetime(year, month, last, 23, 59, 59)
    return start, end


def open_shift(db: Session, staff_id: int) -> Attendance | None:
    return db.scalar(
        select(Attendance).where(
            Attendance.staff_id == staff_id, Attendance.clock_out.is_(None)
        )
    )


def monthly_report(db: Session, staff_id: int, year: int, month: int) -> MonthlyHoursOut:
    """Shifts are attributed to the month in which they were clocked in.
    Shifts that are still open are listed but not counted in total hours."""
    start, end = month_range(year, month)
    records = db.scalars(
        select(Attendance)
        .where(
            Attendance.staff_id == staff_id,
            Attendance.clock_in >= start,
            Attendance.clock_in <= end,
        )
        .order_by(Attendance.clock_in)
    ).all()
    closed = [r for r in records if r.clock_out is not None]
    return MonthlyHoursOut(
        year=year,
        month=month,
        total_hours=round(sum(r.hours for r in closed), 2),
        shifts=len(closed),
        days_worked=len({r.clock_in.date() for r in records}),
        records=[AttendanceOut.model_validate(r) for r in records],
    )


@router.post("/clock-in", response_model=AttendanceOut)
def clock_in(db: Session = Depends(get_db), user: User = Depends(staff_only)):
    if open_shift(db, user.id):
        raise HTTPException(400, "您已經上班打卡，請先下班打卡")
    rec = Attendance(staff_id=user.id, clock_in=now())
    db.add(rec)
    db.commit()
    return rec


@router.post("/clock-out", response_model=AttendanceOut)
def clock_out(db: Session = Depends(get_db), user: User = Depends(staff_only)):
    rec = open_shift(db, user.id)
    if rec is None:
        raise HTTPException(400, "尚未上班打卡")
    rec.clock_out = now()
    db.commit()
    return rec


@router.get("/status", response_model=ClockStatusOut)
def clock_status(db: Session = Depends(get_db), user: User = Depends(staff_only)):
    """目前打卡狀態 + 今日已上班時數 (含進行中的班)。"""
    current = open_shift(db, user.id)
    t = now()
    today_start = t.replace(hour=0, minute=0, second=0)
    today = db.scalars(
        select(Attendance).where(
            Attendance.staff_id == user.id, Attendance.clock_in >= today_start
        )
    ).all()
    seconds = sum(((r.clock_out or t) - r.clock_in).total_seconds() for r in today)
    return ClockStatusOut(
        on_duty=current is not None,
        current=AttendanceOut.model_validate(current) if current else None,
        today_hours=round(seconds / 3600, 2),
    )


@router.get("/monthly", response_model=MonthlyHoursOut)
def my_monthly(
    year: int | None = Query(None, ge=2000, le=2100),
    month: int | None = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
    user: User = Depends(staff_only),
):
    """店員查詢自己每個月的上班時數與打卡紀錄。"""
    t = now()
    return monthly_report(db, user.id, year or t.year, month or t.month)
