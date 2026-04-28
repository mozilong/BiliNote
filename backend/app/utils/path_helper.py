import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


def get_data_dir():
    """获取数据目录，可通过环境变量 DATA_DIR 配置相对或绝对路径"""
    env_data_dir = os.getenv("DATA_DIR")
    if env_data_dir:
        if os.path.isabs(env_data_dir):
            base_dir = env_data_dir
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", env_data_dir))
    elif getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))

    data_path = os.path.join(base_dir, "data")
    os.makedirs(data_path, exist_ok=True)
    return data_path


def get_model_dir(subdir: str = "whisper") -> str:
    """获取模型目录，可通过环境变量 MODEL_DIR 配置"""
    env_model_dir = os.getenv("MODEL_DIR")
    if env_model_dir:
        if os.path.isabs(env_model_dir):
            base_dir = env_model_dir
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", env_model_dir))
    elif getattr(sys, 'frozen', False):
        base_dir = os.path.join(os.getenv("APPDATA") or str(Path.home()), "BiliNote", "models")
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models"))

    path = os.path.join(base_dir, subdir)
    os.makedirs(path, exist_ok=True)
    return path


def get_app_dir(subdir: str = "") -> str:
    """返回一个可写目录，可通过环境变量 APP_DATA_DIR 配置"""
    env_app_dir = os.getenv("APP_DATA_DIR")
    if env_app_dir:
        if os.path.isabs(env_app_dir):
            base_dir = env_app_dir
        else:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../", env_app_dir))
    elif getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))

    full_path = os.path.join(base_dir, subdir)
    os.makedirs(full_path, exist_ok=True)
    return full_path