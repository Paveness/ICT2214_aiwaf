import pymysql
from app.settings import settings

def get_conn():
    return pymysql.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        port=settings.DB_PORT,
        charset="utf8mb4",
        autocommit=True,        # important for logging
        cursorclass=pymysql.cursors.DictCursor,
    )
