import sqlite3

from src.data.env import Env
from src.utils.db_manager import DbManager


def get_db_connection(db_path='backend.db'):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def recreate_tables():
    env: Env = Env()
    
    # with DbManager() as db:
    #     db.execute()
