# Pronóstico de energía industrial

**Planificar el consumo diario de una acería con siete días de anticipación y medir cuánto confiar en esa previsión.**

Python · pandas · SARIMA · Prophet · Streamlit · evaluación temporal

El estudio utiliza consumo real publicado por UCI: 35.040 mediciones de una acería en Corea del Sur, agregadas por fecha a 365 días de2018. La demo es una reconstrucción histórica, no un pronóstico actual conectado a una planta.

## Ejecutar

Con Python3.11–3.14 y uv:

```bash
git clone https://github.com/GzoC/time_series_forecast_analysis.git
cd time_series_forecast_analysis
uv sync --locked --extra dev
uv run --no-sync energy-forecast run
uv run --no-sync energy-forecast dashboard
```

Abre http://127.0.0.1:8504. La primera orden crea los informes y directorios necesarios. También funciona `uv run python run_pipeline.py`. La demo muestra la semana posterior al último día del dataset y permite contrastar un presupuesto diario de energía con el límite superior del pronóstico. No convierte kWh en potencia ni calcula ahorros sin tarifas y restricciones operativas.

## Qué demuestra

- Comparación de referencia semanal, media del mismo día de las últimas ocho semanas, SARIMA y Prophet.
- Cuatro cortes de validación para elegir modelo, cuatro posteriores para calibrar bandas y cuatro de prueba. En cada origen solo se usan observaciones ya disponibles.
- MAE/RMSE en kWh y WAPE; fechas alineadas explícitamente, ceros admitidos y métricas por día del horizonte.
- Bandas basadas en errores anteriores, con cobertura y anchura medidas. No se afirma cobertura garantizada.
- Datos originales con hash y licencia, reportes generados por código, dependencias bloqueadas, CLI instalable y CI.

[Resultados generados](reports/RESULTS.md) · [Metodología y límites](docs/METHODOLOGY.md) · [Procedencia y licencia](data/README.md).

El modelo elegido en validación puede ser superado por otro en prueba: no se cambia la selección después de observarla. El resultado importa más que la complejidad del algoritmo. Las bandas pueden ser amplias; deben evaluarse junto con el error puntual.

## Validación y reproducción

```bash
uv run --no-sync pytest
uv run --no-sync ruff check src tests
uv run --no-sync ruff format --check src tests
uv build
```

La CI ejecuta pruebas, evaluación completa y el wheel fuera del checkout en Python3.11/3.13. Su tarea de contenedor construye la imagen, genera informes y comprueba salud HTTP. Esto no reemplaza la revisión visual de la aplicación.

```bash
docker compose up --build
```

[Estado de implementación y evidencia pendiente](docs/IMPLEMENTATION_STATUS.md). Historial original conservado en Git; el experimento de ventas de origen no documentado permanece en el commit266ada82b7fd25bce524667ca801a2d44290910c.

English: Reproducible daily industrial energy forecasting with chronological model selection, seasonal baselines, calibrated error bands and an explicit historical planning scenario.

Autor: [GzoC](https://github.com/GzoC). Código MIT. Fuente: V E, S., Shin, C., & Cho, Y. (2021), Steel Industry Energy Consumption, UCI, DOI10.24432/C52G8C, CC BY4.0.
