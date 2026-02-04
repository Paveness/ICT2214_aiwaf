import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Response, Request
from app.db.db_config import get_conn
from app.models.user_model import UserModel

COOKIE_NAME = "auth_session"
SESSION_TTL_SECONDS = 3600  # 1 hour


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _hash_token(token: str) -> str:
    # Store only hash(token) in DB
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_or_replace_session(user_id: int, request=None) -> str:
    raw_token = secrets.token_urlsafe(32)
    session_id = _hash_token(raw_token)

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    expires = (datetime.now(timezone.utc) + timedelta(seconds=SESSION_TTL_SECONDS)).replace(tzinfo=None)

    user_agent = request.headers.get("user-agent")[:255] if request else None
    ip_address = request.client.host if (request and request.client) else None

    sql = """
    INSERT INTO sessions (session_id, user_id, expires_at, last_seen, user_agent, ip_address, is_revoked)
    VALUES (%s, %s, %s, %s, %s, %s, FALSE)
    ON DUPLICATE KEY UPDATE
        session_id = VALUES(session_id),
        expires_at = VALUES(expires_at),
        last_seen = VALUES(last_seen),
        user_agent = VALUES(user_agent),
        ip_address = VALUES(ip_address),
        is_revoked = FALSE,
        created_at = CURRENT_TIMESTAMP
    """

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (session_id, user_id, expires, now, user_agent, ip_address))
        conn.commit()
    finally:
        conn.close()

    return raw_token

def _validate_db_session(raw_token: str):
    session_id = _hash_token(raw_token)
    now = _now_utc().replace(tzinfo=None)

    sql = """
    SELECT s.session_id, s.user_id, s.expires_at, s.is_revoked,
           u.username, u.role
    FROM sessions s
    JOIN users u ON u.user_id = s.user_id
    WHERE s.session_id = %s
    LIMIT 1
    """

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (session_id,))
            row = cur.fetchone()

            if not row:
                return None

            if row["is_revoked"]:
                return None

            if row["expires_at"] <= now:
                # optional: cleanup expired session row immediately
                cur.execute("DELETE FROM sessions WHERE session_id = %s", (session_id,))
                return None

            # update last_seen
            cur.execute(
                "UPDATE sessions SET last_seen = %s WHERE session_id = %s",
                (now, session_id),
            )

            return {
                "user_id": row["user_id"],
                "username": row["username"],
                "role": row["role"],
            }
    finally:
        conn.close()


def _revoke_db_session(raw_token: str):
    session_id = _hash_token(raw_token)
    sql = "UPDATE sessions SET is_revoked = TRUE WHERE session_id = %s"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (session_id,))
    finally:
        conn.close()


# ===============================
# Controller actions
# ===============================

def login_controller(username: str, password: str, response: Response, request: Request):
    user = UserModel.authenticate(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    raw_token = create_or_replace_session(user_id=user["user_id"], request=request)

    response.set_cookie(
        key=COOKIE_NAME,
        value=raw_token,        # cookie gets RAW token
        httponly=True,
        secure=False,           # True in prod (HTTPS)
        samesite="lax",
        path="/",
        max_age=SESSION_TTL_SECONDS,
    )

    return {
        "status": "ok",
        "user": {"username": user["username"], "role": user.get("role", "analyst")},
    }


def auth_check_controller(request: Request):
    raw_token = request.cookies.get(COOKIE_NAME)
    if not raw_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = _validate_db_session(raw_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {"ok": True, "user": {"username": user["username"], "role": user["role"]}}


def logout_controller(request: Request, response: Response):
    raw_token = request.cookies.get(COOKIE_NAME)
    if raw_token:
        _revoke_db_session(raw_token)

    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"status": "ok"}
