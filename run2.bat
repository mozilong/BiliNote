@echo off
chcp 65001 >nul 2>&1
echo ==============================================
echo            BiliNote 一键启动脚本 (Win10)
echo ==============================================

:: 已填入你的 conda 实际安装路径
set CONDA_PATH=C:\ProgramData\anaconda3

:: 检查 conda 激活脚本是否存在
if not exist "%CONDA_PATH%\Scripts\activate.bat" (
    echo 错误：未找到 conda 激活脚本！
    echo 检查路径：%CONDA_PATH%\Scripts\activate.bat
    pause
    exit /b 1
)

:: 激活虚拟环境 bilinote（激活后不阻塞，直接启动服务）
echo [1/4] 激活虚拟环境 bilinote...
call "%CONDA_PATH%\Scripts\activate.bat" bilinote >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：激活虚拟环境 bilinote 失败！
    echo 请确认环境名称是否为 bilinote（若为 bilinot 请修改脚本中对应的名称）
    pause
    exit /b 1
)

:: 启动后端服务（使用 start /b 后台启动，窗口启动后自动关闭提示，仅保留服务进程）
echo [2/4] 启动后端服务...
if not exist "D:\BiliNote\backend\main.py" (
    echo 错误：后端文件 D:\BiliNote\backend\main.py 不存在！
    pause
    exit /b 1
)
start "BiliNote 后端服务" cmd /c "cd /d D:\BiliNote\backend && python main.py"

:: 启动前端服务（同理后台启动）
echo [3/4] 启动前端服务...
if not exist "D:\BiliNote\BillNote_frontend" (
    echo 错误：前端目录 D:\BiliNote\BillNote_frontend 不存在！
    pause
    exit /b 1
)
start "BiliNote 前端服务" cmd /c "cd /d D:\BiliNote\BillNote_frontend && pnpm dev"

:: 输出访问地址并延迟2秒后关闭脚本窗口
echo [4/4] 服务启动完成！
echo ==============================================
echo 🔗 后端访问地址：http://127.0.0.1:8483
echo 🔗 前端访问地址：http://127.0.0.1:3015
echo ==============================================
echo 提示：服务已后台启动，此窗口将在2秒后自动关闭...
timeout /t 2 /nobreak >nul
exit