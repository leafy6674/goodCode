from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import attendance, auth, manager, orders

Base.metadata.create_all(bind=engine)

app = FastAPI(title="飲料店系統 API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(attendance.router)
app.include_router(manager.router)


@app.get("/api/health")
def health():
    return {"ok": True}
