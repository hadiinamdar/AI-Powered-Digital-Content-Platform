@echo off
title JZD Content Studio

start "JZD Backend" cmd /k "cd /d D:\Inamdar\new jzd\backend && call .venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"

timeout /t 5 /nobreak >nul

start "" "D:\Inamdar\new jzd\frontend\index.html"