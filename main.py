from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, SessionLocal
from models import Tenant, Widget
from routes.chat import router as chat_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(chat_router, prefix="/api")

def seed():
    db = SessionLocal()

    if not db.query(Widget).filter(Widget.id == "test123").first():
        tenant = Tenant(name="Test Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        widget = Widget(
            id="test123",
            tenant_id=tenant.id,
            primary_color="#2563eb"
        )
        db.add(widget)
        db.commit()

    db.close()

seed()