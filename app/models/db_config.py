import os
import pymysql
from dotenv import load_dotenv

# Load credentials from the .env file (assuming it's in the server folder or root)
# Adjust the path if your .env is elsewhere
load_dotenv(dotenv_path='../../server/.env')

def get_db_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'neurowaf_db'),
            port=int(os.getenv('DB_PORT', 3306)),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True # Important for real-time inserts
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"❌ Database Connection Error: {e}")
        return None