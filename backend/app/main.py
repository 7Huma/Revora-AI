from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.db.database import Base, engine
from app.api.routes import health, payments, checkouts, subscriptions, receivables, recovery, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Revora AI API",
    version="1.1.0",
    description="Detect revenue at risk, diagnose causes, choose interventions and execute recovery workflows."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(checkouts.router, prefix="/checkouts", tags=["Checkouts"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
app.include_router(receivables.router, prefix="/receivables", tags=["Receivables"])
app.include_router(recovery.router, prefix="/recovery", tags=["Recovery"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
