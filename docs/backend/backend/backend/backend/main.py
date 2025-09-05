import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routers import emails, stats, kb, responses
from app.db import init_db
from apscheduler.schedulers.background import BackgroundScheduler
from app.worker import fetch_and_process_emails

load_dotenv()
app = FastAPI(title="AI Communication Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

scheduler = BackgroundScheduler()
interval = int(os.getenv("FETCH_INTERVAL_SECONDS", "120"))
scheduler.add_job(fetch_and_process_emails, "interval", seconds=interval, id="fetch_emails", replace_existing=True)
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(kb.router, prefix="/api/kb", tags=["kb"])
app.include_router(responses.router, prefix="/api/responses", tags=["responses"])

@app.get("/")
async def root():
    return {"ok": True, "app": "AI Communication Assistant"}
