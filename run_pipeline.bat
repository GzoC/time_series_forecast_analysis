@echo off
cd /d D:\gzo\myProjects\dataAnalyst\projects\time_series_forecast_analysis
call .venv_forecasting\Scripts\activate
python run_pipeline.py
pause
