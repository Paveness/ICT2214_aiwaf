from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers.proxy_controller import router as proxy_router
from app.services.proxy_service import ProxyService
from app.services.logging_service import LoggingService
from app.waf.ai_model import AIAnomalyScorer
from app.api.routes import router  # This is the new dashboard logic

app = FastAPI(title="AIWAF Proxy (V1)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],     # POST, GET, OPTIONS, etc
    allow_headers=["*"],     # Content-Type, Authorization, etc
)

app.include_router(router, prefix="/api")
app.include_router(proxy_router)

proxy_service = ProxyService()
logging_service = LoggingService()

@app.on_event("startup")
async def on_startup():
    print("🚀 Starting AIWAF Proxy & Dashboard API...")
    
    # Load AI Model
    anomaly_ai = AIAnomalyScorer()
    anomaly_ai.load()
    app.state.anomaly_ai_scorer = anomaly_ai
    
    # Start Proxy Service
    await proxy_service.startup()
    

async def on_shutdown():
    await proxy_service.shutdown()

app.state.proxy_service = proxy_service
app.state.logging_service = logging_service