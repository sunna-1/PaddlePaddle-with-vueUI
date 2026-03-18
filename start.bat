@echo off
chcp 65001 >nul
echo ====================================
echo 交通状况分析系统 - 启动脚本
echo ====================================
echo.

REM 检查 conda 环境
echo [1/4] 检查 conda 环境...
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 conda 命令，请先安装 Anaconda 或 Miniconda
    pause
    exit /b 1
)

REM 激活 pp 环境并检查
echo [2/4] 激活 pp conda 环境...
call conda activate pp
if %errorlevel% neq 0 (
    echo 错误：无法激活 pp conda 环境，请先创建该环境
    echo 运行：conda create -n pp python=3.8 paddlepaddle-gpu
    pause
    exit /b 1
)

REM 启动后端
echo [3/4] 启动后端服务...
start "后端服务" cmd /k "cd /d %~dp0 && conda activate pp && python app.py"
timeout /t 5 /nobreak >nul

REM 启动前端
echo [4/4] 启动前端服务...
cd frontend
start "前端服务" cmd /k "npm run dev"

echo.
echo ====================================
echo 服务启动完成！
echo 后端：http://localhost:5000
echo 前端：http://localhost:3000
echo ====================================
echo.
pause
