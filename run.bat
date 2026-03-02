@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: 已填入你的 conda 实际安装路径
set CONDA_PATH=C:\ProgramData\anaconda3

:: 检查 conda 激活脚本是否存在（仅错误时提示）
if not exist "%CONDA_PATH%\Scripts\activate.bat" (
    echo 错误：未找到 conda 激活脚本！
    echo 检查路径：%CONDA_PATH%\Scripts\activate.bat
    pause
    exit /b 1
)

:: 激活虚拟环境 bilinote（静默，屏蔽输出）
call "%CONDA_PATH%\Scripts\activate.bat" bilinote >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：激活虚拟环境 bilinote 失败！
    echo 请确认环境名称是否为 bilinote（若名称不符请修改脚本）
    pause
    exit /b 1
)

:: 启动后端服务（后台运行，无窗口，屏蔽输出）
if not exist "D:\BiliNote\backend\main.py" (
    echo 错误：后端文件 D:\BiliNote\backend\main.py 不存在！
    pause
    exit /b 1
)
start /b cmd /c "cd /d D:\BiliNote\backend && python main.py >nul 2>&1"

:: 启动前端服务（后台运行，无窗口，屏蔽输出）
if not exist "D:\BiliNote\BillNote_frontend" (
    echo 错误：前端目录 D:\BiliNote\BillNote_frontend 不存在！
    pause
    exit /b 1
)
start /b cmd /c "cd /d D:\BiliNote\BillNote_frontend && pnpm dev >nul 2>&1"

:: 极简提示（可选，也可删除这几行彻底无提示）
echo BiliNote 服务已静默启动！
echo 🔗 后端：http://127.0.0.1:8483
echo 🔗 前端：http://127.0.0.1:3015
echo （关闭此窗口不会终止服务，如需停止请用任务管理器结束 python/node 进程）
timeout /t 3 /nobreak >nul  :: 停留3秒让你看到提示，可删除
exit /b 0