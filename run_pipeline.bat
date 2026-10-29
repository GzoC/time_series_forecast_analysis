@echo off
cd /d "%~dp0"
uv run --locked energy-forecast run
