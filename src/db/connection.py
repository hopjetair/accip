import os
from psycopg_pool import AsyncConnectionPool
from contextlib import asynccontextmanager
from config import *

# Construct DSN from environment or fallback to config values
dsn = (
    f"host={os.getenv(const_fieldname_db_host, db_host)} "
    f"port={os.getenv(const_fieldname_db_port, db_port)} "
    f"dbname={os.getenv(const_fieldname_db_name, db_name)} "
    f"user={os.getenv(const_fieldname_db_user, db_user)} "
    f"password={os.getenv(const_fieldname_db_pass, db_pass)}"
)


db_pool = AsyncConnectionPool(conninfo=dsn, max_size=20, min_size=5)


async def open_db_pool():
    """Open the database connection pool"""
    if db_pool:
        await db_pool.open()


async def close_db_pool():
    """Close the database connection pool"""
    if db_pool:
        await db_pool.close()


@asynccontextmanager
async def get_db_connection():
    """
    Acquire a connection from the async pool. (No changes needed here)
    """
    try:
        conn = await db_pool.getconn()
    except Exception as e:
        raise Exception(f"Failed to acquire DB connection: {e}")
    
    try:
        yield conn
    finally:
        await db_pool.putconn(conn)

