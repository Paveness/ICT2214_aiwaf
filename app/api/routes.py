from fastapi import APIRouter, Response, Request
from pydantic import BaseModel

from app.controllers.auth_controller import (
    login_controller,
    auth_check_controller,
    logout_controller,
)
from app.controllers.waf_controller import (
    setup_waf_controller
)
from app.controllers.logs_controller import LogsController

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class SetupWAFRequest(BaseModel):
    target_host: str
    proxy_port: int
    login_endpoint: str | None = None
    excluded_endpoints: str | None = None
    username: str
    password: str

@router.post("/login")
def login(payload: LoginRequest, request: Request, response: Response):
    return login_controller(payload.username, payload.password, response, request)

@router.get("/auth/check")
def auth_check(request: Request):
    return auth_check_controller(request)

@router.post("/logout")
def logout(request: Request, response: Response):
    return logout_controller(request, response)

@router.post("/setupwaf")
def setupwaf(payload: SetupWAFRequest):
    print(payload)
    return setup_waf_controller(payload)

@router.get("/logs")
def get_logs(
    search: str = "",
    attack_type: str = "All",
    limit: int = 20,
    page: int = 1,
    time_mode: str = "preset",
    time_preset: str = "24h",
    start_date: str | None = None,
    end_date: str | None = None,
):
    return LogsController.get_logs(
        search=search,
        attack_type=attack_type,
        limit=limit,
        page=page,
        time_mode=time_mode,
        time_preset=time_preset,
        start_date=start_date,
        end_date=end_date,
    )

@router.get("/filters")
def filters():
    return LogsController.get_attack_types()
