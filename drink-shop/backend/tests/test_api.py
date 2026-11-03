import os
from datetime import timedelta

os.environ["DATABASE_URL"] = "sqlite:///./test_drink_shop.db"

import pytest
from fastapi.testclient import TestClient

from app.config import now
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Attendance, Order, Product, Role, User
from app.security import hash_password

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    pw = hash_password("123456")
    db.add_all([
        User(username="boss", password_hash=pw, name="店長", role=Role.manager.value),
        User(username="clerk", password_hash=pw, name="店員", role=Role.staff.value),
        User(username="cust", password_hash=pw, name="客人", role=Role.customer.value),
        Product(name="珍珠奶茶", category="奶茶", price=55),
    ])
    db.commit()
    db.close()
    yield


def token(username):
    r = client.post("/api/auth/login", json={"username": username, "password": "123456"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_register_and_login():
    r = client.post("/api/auth/register",
                    json={"username": "newbie", "password": "secret1", "name": "新人"})
    assert r.status_code == 201
    assert r.json()["user"]["role"] == "customer"
    assert client.post("/api/auth/login",
                       json={"username": "newbie", "password": "wrong"}).status_code == 401
    me = client.get("/api/auth/me", headers=token("cust"))
    assert me.json()["username"] == "cust"


def test_my_orders_only_last_12_months():
    h = token("cust")
    r = client.post("/api/orders", headers=h,
                    json={"items": [{"product_id": 1, "quantity": 2, "sugar": "半糖", "ice": "少冰"}]})
    assert r.status_code == 201 and r.json()["total"] == 110

    db = SessionLocal()
    cust = db.query(User).filter_by(username="cust").one()
    db.add(Order(customer_id=cust.id, created_at=now() - timedelta(days=400), total=99))
    db.add(Order(customer_id=cust.id, created_at=now() - timedelta(days=300), total=50))
    db.commit()
    db.close()

    data = client.get("/api/orders/me", headers=h).json()
    assert data["count"] == 2
    assert data["total_spent"] == 160


def test_clock_in_out_and_monthly_hours():
    h = token("clerk")
    assert client.get("/api/attendance/status", headers=h).json()["on_duty"] is False
    assert client.post("/api/attendance/clock-in", headers=h).status_code == 200
    assert client.post("/api/attendance/clock-in", headers=h).status_code == 400
    assert client.get("/api/attendance/status", headers=h).json()["on_duty"] is True
    assert client.post("/api/attendance/clock-out", headers=h).status_code == 200

    db = SessionLocal()
    clerk = db.query(User).filter_by(username="clerk").one()
    t = now().replace(day=1, hour=9, minute=0, second=0)
    db.add(Attendance(staff_id=clerk.id, clock_in=t, clock_out=t + timedelta(hours=8)))
    db.commit()
    db.close()

    rep = client.get("/api/attendance/monthly", headers=h).json()
    assert rep["shifts"] == 2
    assert 8 <= rep["total_hours"] < 8.1


def test_role_permissions():
    assert client.get("/api/manager/summary", headers=token("cust")).status_code == 403
    assert client.get("/api/manager/summary", headers=token("clerk")).status_code == 403
    assert client.post("/api/attendance/clock-in", headers=token("cust")).status_code == 403
    assert client.get("/api/orders/me").status_code == 401


def test_manager_reports():
    client.post("/api/orders", headers=token("cust"),
                json={"items": [{"product_id": 1, "quantity": 3}]})
    h = token("boss")
    s = client.get("/api/manager/summary", headers=h).json()
    assert s["order_count"] == 1 and s["revenue"] == 165 and s["cups_sold"] == 3
    assert s["top_products"][0]["product_name"] == "珍珠奶茶"
    m = client.get("/api/manager/monthly-revenue", headers=h).json()
    assert len(m) == 12 and m[-1]["revenue"] == 165
    rows = client.get("/api/manager/staff-hours", headers=h).json()
    assert {r["username"] for r in rows} == {"boss", "clerk"}
    r = client.post("/api/manager/staff", headers=h,
                    json={"username": "clerk2", "password": "123456", "name": "新店員"})
    assert r.status_code == 201 and r.json()["role"] == "staff"
