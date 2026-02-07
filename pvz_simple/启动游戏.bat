@echo off
chcp 65001 >nul
title 植物大战僵尸简化版
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo 游戏运行出错！
    echo 请确保已安装 pygame 库：pip install pygame
    pause
)

