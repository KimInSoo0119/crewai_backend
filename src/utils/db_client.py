import os
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("DB_HOST")
PORT = int(os.getenv("DB_PORT", 5432))
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
DBNAME = os.getenv("DB_NAME")

db_pool = None

def init_db_pool(minconn=1, maxconn=10):
    global db_pool
    if not db_pool:
        db_pool = pool.SimpleConnectionPool(
            minconn,
            maxconn,
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            dbname=DBNAME,
            cursor_factory=RealDictCursor 
        )

def get_db_connection():
    if not db_pool:
        init_db_pool()
    return db_pool.getconn()  

def release_db_connection(conn):
    if db_pool and conn:
        db_pool.putconn(conn) 
