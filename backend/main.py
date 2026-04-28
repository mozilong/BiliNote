import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.db.init_db import init_db
from app.db.provider_dao import seed_default_providers
from app.exceptions.exception_handlers import register_exception_handlers
from app.utils.logger import get_logger
from app import create_app
from app.transcriber.transcriber_provider import get_transcriber
from events import register_handler
from ffmpeg_helper import ensure_ffmpeg_or_raise

logger = get_logger(__name__)
load_dotenv()

# 读取 .env 中的路径 - 可通过环境变量配置以支持多实例
static_path = os.getenv('STATIC', '/static')
uploads_path = os.getenv('UPLOADS', '/uploads')
out_dir = os.getenv('OUT_DIR', './static/screenshots')

# 静态文件目录 - 可通过环境变量配置
static_dir = os.getenv('STATIC_DIR', 'static')
uploads_dir = os.getenv('UPLOADS_DIR', 'uploads')

# 自动创建本地目录
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

@asynccontextmanager
async def lifespan(app: FastAPI):
    register_handler()
    init_db()
    get_transcriber(transcriber_type=os.getenv("TRANSCRIBER_TYPE", "fast-whisper"))
    seed_default_providers()
    yield

app = create_app(lifespan=lifespan)
# 支持的来源 - 包含本地和常见部署地址
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://tauri.localhost",
    # 本地开发端口
    "http://localhost:3015",
    "http://127.0.0.1:3015",
    # 服务器公网 IP
    "http://111.14.140.78",
    "http://111.14.140.78:3015",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)
app.mount(static_path, StaticFiles(directory=static_dir), name="static")
app.mount(uploads_path, StaticFiles(directory=uploads_dir), name="uploads")

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 8483))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, reload=False)
