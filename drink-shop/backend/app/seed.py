"""建立示範資料：python -m app.seed  (會清空現有資料)"""
import random
from datetime import timedelta

from .config import months_ago, now
from .database import Base, SessionLocal, engine
from .models import Attendance, Order, OrderItem, Product, Role, User
from .security import hash_password

MENU = [
    ("茶類", "茉莉綠茶", 30), ("茶類", "阿薩姆紅茶", 30), ("茶類", "四季春青茶", 35),
    ("茶類", "冬瓜檸檬", 45),
    ("奶茶", "珍珠奶茶", 55), ("奶茶", "波霸奶茶", 55), ("奶茶", "黑糖鮮奶", 65),
    ("奶茶", "烏龍拿鐵", 60),
    ("果茶", "百香雙響炮", 55), ("果茶", "葡萄柚綠", 60), ("果茶", "芒果冰沙", 70),
    ("特調", "多多綠茶", 45), ("特調", "蜂蜜檸檬", 50),
]
SUGARS = ["正常糖", "少糖", "半糖", "微糖", "無糖"]
ICES = ["正常冰", "少冰", "微冰", "去冰", "熱"]


def run(seed: int = 42):
    rnd = random.Random(seed)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    pw = hash_password("123456")
    manager = User(username="manager", password_hash=pw, name="王店長", role=Role.manager.value)
    staff = [
        User(username=f"staff{i}", password_hash=pw, name=n, role=Role.staff.value)
        for i, n in enumerate(["林小美", "陳阿明", "張小華"], start=1)
    ]
    customers = [
        User(username=f"member{i}", password_hash=pw, name=n, phone=f"09{i:08d}",
             role=Role.customer.value)
        for i, n in enumerate(["李大同", "黃小玲", "吳志明", "周佳穎", "蔡宗翰"], start=1)
    ]
    db.add_all([manager, *staff, *customers])
    products = [Product(category=c, name=n, price=p) for c, n, p in MENU]
    db.add_all(products)
    db.flush()

    t = now()
    start = months_ago(t, 15).replace(hour=0, minute=0, second=0)  # 15 個月，可驗證 12 個月過濾

    # 訂單
    day = start
    while day.date() <= t.date():
        for _ in range(rnd.randint(15, 40)):
            ts = day.replace(hour=rnd.randint(10, 21), minute=rnd.randint(0, 59),
                             second=rnd.randint(0, 59))
            if ts > t:
                continue
            cust = rnd.choice(customers) if rnd.random() < 0.35 else None
            order = Order(customer_id=cust.id if cust else None, created_at=ts)
            total = 0
            for _ in range(rnd.randint(1, 4)):
                p = rnd.choice(products)
                q = rnd.randint(1, 3)
                order.items.append(OrderItem(
                    product_id=p.id, product_name=p.name, unit_price=p.price, quantity=q,
                    sugar=rnd.choice(SUGARS), ice=rnd.choice(ICES)))
                total += p.price * q
            order.total = total
            db.add(order)
        day += timedelta(days=1)

    # 打卡紀錄 (近 4 個月)
    day = months_ago(t, 4).replace(hour=0, minute=0, second=0)
    while day.date() < t.date():
        for s in [manager, *staff]:
            if rnd.random() < 0.3:
                continue  # 休假
            shift_start = rnd.choice([9, 10, 14, 15])
            cin = day.replace(hour=shift_start, minute=rnd.randint(0, 15))
            cout = cin + timedelta(hours=rnd.choice([4, 6, 8]), minutes=rnd.randint(-10, 20))
            db.add(Attendance(staff_id=s.id, clock_in=cin, clock_out=cout))
        day += timedelta(days=1)

    db.commit()
    db.close()
    print("示範資料建立完成。所有帳號密碼皆為 123456：")
    print("  店長: manager   店員: staff1~staff3   會員: member1~member5")


if __name__ == "__main__":
    run()
