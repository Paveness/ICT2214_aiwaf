import pymysql

def test_mysql_connection():
    try:
        conn = pymysql.connect(
            host="127.0.0.1",     # change if needed
            user="your_user",
            password="your_password",
            database="your_database",  # optional, but recommended
            port=3306,
            connect_timeout=5
        )

        print("✅ MySQL connection successful!")

        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()
            print(f"🛢️ MySQL version: {version[0]}")

        conn.close()
        print("🔌 Connection closed cleanly.")

    except pymysql.MySQLError as e:
        print("❌ MySQL connection failed!")
        print(f"Error: {e}")

if name == "main":
    test_mysql_connection()