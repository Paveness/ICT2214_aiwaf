from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- IMPORT THIS
from app.controllers.proxy_controller import router as proxy_router
from app.services.proxy_service import ProxyService
from app.services.logging_service import LoggingService
from app.waf.ai_model import AIAnomalyScorer
from app.api.routes import router  # This is the new dashboard logic

app = FastAPI(title="AIWAF Proxy (V1)")

# --- 1. ENABLE CORS (Crucial for React Frontend) ---
# This allows http://localhost:5173 to send requests to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow GET, POST, etc.
    allow_headers=["*"],
)

# --- 2. REGISTER ROUTES ---
# Dashboard API (Login, Logs, Filters)
app.include_router(router, prefix="/api") 
# Proxy Traffic Handler
app.include_router(proxy_router)

# --- 3. SERVICE INITIALIZATION ---
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

@app.on_event("shutdown")
async def on_shutdown():
    print("🛑 Shutting down...")
    await proxy_service.shutdown()

app.state.proxy_service = proxy_service
app.state.logging_service = logging_service

if __name__ == "__main__":
    import uvicorn
    # Run on port 5000 to match your old Node backend configuration
    uvicorn.run(app, host="0.0.0.0", port=5000)