from fastapi import APIRouter, Response, Request
from pydantic import BaseModel
from typing import Literal, Optional

from app.controllers.auth_controller import (
    login_controller,
    auth_check_controller,
    logout_controller,
)
from app.controllers.waf_controller import (
    setup_waf_controller
)
from app.controllers.logs_controller import LogsController
from app.controllers.policy_controller import PolicyController

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

class PolicyRuleCreate(BaseModel):
    list_type: Literal["whitelist", "blacklist"]
    ip_address: str
    reason: Optional[str] = None
    created_by: Optional[str] = None
    expires_at: Optional[str] = None

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

@router.get("/policy/entries")
def list_policy_entries(list_type: Optional[str] = None):
    return PolicyController.list_rules(list_type)

@router.post("/policy/entries")
def create_policy_entry(payload: PolicyRuleCreate):
    return PolicyController.create_rule(payload.model_dump())

@router.delete("/policy/entries/{rule_id}")
def delete_policy_entry(rule_id: int):
    return PolicyController.delete_rule(rule_id)
