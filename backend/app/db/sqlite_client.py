import os
import sqlite3
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bili_note.db")


def get_connection():
    """获取 SQLite 连接，支持通过 DATABASE_URL 环境变量配置"""
    if DATABASE_URL.startswith("sqlite"):
        parsed = urlparse(DATABASE_URL)
        db_path = parsed.path
        if not db_path:
            db_path = "bili_note.db"
        return sqlite3.connect(db_path)
    else:
        return sqlite3.connect(DATABASE_URL)
