# app/controllers/waf_controller.py

import bcrypt
from fastapi import HTTPException
from app.db.db_config import get_conn


def setup_waf_controller(payload) -> dict:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # 1) Create WAF instance FIRST (so we have waf_id)
            cur.execute(
                """
                INSERT INTO waf_instances (target_host, proxy_port, is_active)
                VALUES (%s, %s, TRUE)
                """,
                (payload.target_host, payload.proxy_port),
            )
            waf_id = cur.lastrowid

            # 2) Create admin user tied to this waf_id
            password_hash = bcrypt.hashpw(
                payload.password.encode("utf-8"),
                bcrypt.gensalt(),
            ).decode("utf-8")

            cur.execute(
                """
                INSERT INTO users (waf_id, username, password_hash, role)
                VALUES (%s, %s, %s, 'admin')
                """,
                (waf_id, payload.username, password_hash),
            )
            user_id = cur.lastrowid

            # 3) Create crawler settings tied to this waf_id
            cur.execute(
                """
                INSERT INTO crawler_settings (waf_id, login_endpoint, excluded_endpoints)
                VALUES (%s, %s, %s)
                """,
                (waf_id, payload.login_endpoint, payload.excluded_endpoints),
            )

        conn.commit()

        return {
            "status": "ok",
            "message": "Neuro-WAF setup completed",
            "waf_id": waf_id,
            "admin_user_id": user_id,
            "admin_user": payload.username,
        }

    except Exception as e:
        conn.rollback()
        msg = str(e)

        # nicer error for duplicate username
        if "Duplicate entry" in msg and "users.username" in msg:
            raise HTTPException(status_code=409, detail="Username already exists")

        raise HTTPException(status_code=400, detail=f"WAF setup failed: {msg}")

    finally:
        conn.close()
