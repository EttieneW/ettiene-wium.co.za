@echo off
title ettiene-wium.com
cd /d "%~dp0"
echo Public CV:  http://localhost:8097
echo Press Ctrl+C to stop.
py -3 api\handler.py
if errorlevel 1 python api\handler.py
