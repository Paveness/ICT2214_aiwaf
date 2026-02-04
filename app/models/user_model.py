# app/models/user_model.py

import bcrypt
from app.db.db_config import get_conn

class UserModel:
    @staticmethod
    def authenticate(username: str, password: str):
        sql = """
        SELECT user_id, username, password_hash, role
        FROM users
        WHERE username = %s
        LIMIT 1
        """
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (username,))
                user = cur.fetchone()
        finally:
            conn.close()

        if not user:
            return None

        stored = user["password_hash"]

        # if password == stored :
        #     return user
            
        if isinstance(stored, str):
            stored = stored.encode()

        if not bcrypt.checkpw(password.encode(), stored):
            return None

        return user
