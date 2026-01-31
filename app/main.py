from fastapi import FastAPI
from app.controllers.proxy_controller import router as proxy_router
from app.services.proxy_service import ProxyService
from app.services.logging_service import LoggingService
from app.waf.ai_model import AIAnomalyScorer

proxy_service = ProxyService()
logging_service = LoggingService()

app = FastAPI(title="AIWAF Proxy (V1)")

@app.on_event("startup")
async def on_startup():
    anomaly_ai = AIAnomalyScorer()
    anomaly_ai.load()
    app.state.anomaly_ai_scorer = anomaly_ai
    await proxy_service.startup()

@app.on_event("shutdown")
async def on_shutdown():
    await proxy_service.shutdown()

app.state.proxy_service = proxy_service
app.state.logging_service = logging_service

app.include_router(proxy_router)
