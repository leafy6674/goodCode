# 🧋 好茶飲料店系統

Python (FastAPI) 後端 + React (Vite) 前端的飲料店網站。

## 功能

| 角色 | 功能 |
| --- | --- |
| 所有人 | 瀏覽菜單 |
| 客戶會員 | 註冊／登入、線上點餐 (甜度、冰塊、數量)、**查詢自己近 12 個月內所有訂單**（含明細、月份篩選、累計消費） |
| 店員 | 登入、**上班／下班打卡**、查看目前打卡狀態與今日工時、**查詢每個月上班時數**與每筆打卡紀錄 |
| 店長 | **營運資料查詢**：營業額、訂單數、客單價、售出杯數、會員訂單比例、每日營收、熱銷商品 Top 10、時段分佈、近 12 個月營收；查看所有店員當月工時、上班狀態與打卡明細；新增店員帳號。店長本身也可打卡 |

登入使用 JWT，密碼以 PBKDF2-SHA256 加鹽雜湊儲存；API 依角色檢查權限 (401/403)。

## 專案結構

```
drink-shop/
├── backend/                FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   │   ├── main.py         應用程式進入點
│   │   ├── models.py       資料表：User / Product / Order / OrderItem / Attendance
│   │   ├── security.py     密碼雜湊、JWT、角色權限
│   │   ├── seed.py         示範資料
│   │   └── routers/        auth / orders / attendance / manager
│   └── tests/test_api.py
└── frontend/               React 18 + React Router + Vite
    └── src/pages/          Login / Menu / MyOrders / Staff / Manager
```

## 啟動

需要 Python 3.10+ 與 Node.js 18+。

```bash
cd backend
pip install -r requirements.txt
python -m app.seed            # 建立示範資料 (會清空資料庫)
uvicorn app.main:app --reload --port 8000
```

另開一個終端機：

```bash
cd frontend
npm install
npm run dev                   # http://localhost:5173 (/api 會 proxy 到 8000)
```

API 文件：http://localhost:8000/docs

### 示範帳號 (密碼皆為 `123456`)

- 店長：`manager`
- 店員：`staff1`、`staff2`、`staff3`
- 會員：`member1` ~ `member5`

示範資料包含近 15 個月的訂單（用來確認會員只會看到 12 個月內的訂單）和近 4 個月的打卡紀錄。

### 測試

```bash
cd backend && python -m pytest -q
```

## 主要 API

| Method | Path | 權限 | 說明 |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | — | 註冊會員 |
| POST | `/api/auth/login` | — | 登入，取得 token |
| GET | `/api/auth/me` | 登入 | 目前使用者 |
| GET | `/api/products` | — | 菜單 |
| POST | `/api/orders` | 會員 | 下單 |
| GET | `/api/orders/me` | 登入 | 自己近 12 個月的訂單 |
| POST | `/api/attendance/clock-in` / `clock-out` | 店員/店長 | 上班／下班打卡 |
| GET | `/api/attendance/status` | 店員/店長 | 目前打卡狀態 |
| GET | `/api/attendance/monthly?year=&month=` | 店員/店長 | 自己的月工時 |
| GET | `/api/manager/summary?start=&end=` | 店長 | 營運摘要 |
| GET | `/api/manager/monthly-revenue?months=12` | 店長 | 每月營收 |
| GET | `/api/manager/staff-hours?year=&month=` | 店長 | 所有店員月工時 |
| GET | `/api/manager/staff/{id}/monthly` | 店長 | 單一店員打卡明細 |
| POST | `/api/manager/staff` | 店長 | 新增店員 |

## 說明

- 時間以店家時區 `Asia/Taipei` 計算，可用環境變數 `SHOP_TZ` 調整。
- 工時以「上班打卡」那天所在的月份計算；還沒下班打卡的班會列出來，但不算進總工時。
- 上線前請設定環境變數 `SECRET_KEY`；`DATABASE_URL` 可換成 PostgreSQL 等資料庫。
