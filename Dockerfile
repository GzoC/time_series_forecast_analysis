FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir --require-hashes -r requirements.txt && pip install --no-deps .
COPY data/raw/Steel_industry_data.csv ./data/raw/Steel_industry_data.csv
RUN energy-forecast run
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8504
CMD ["python", "-m", "streamlit", "run", "src/energy_forecast/dashboard.py", "--server.address=0.0.0.0", "--server.port=8504", "--server.headless=true", "--browser.gatherUsageStats=false"]
