# run_pipeline.py

import os
from src.ingestion.load_data import load_raw_data
from src.preprocessing.clean_data import clean_sales_data
from src.modeling.arima_model import train_test_split as arima_split, train_arima, forecast_arima, select_arima_order, evaluate_model as evaluate_arima
from src.modeling.prophet_model import train_test_split as prophet_split, train_prophet, forecast_prophet, evaluate_model as evaluate_prophet, load_clean_data as load_for_prophet
import pandas as pd

# --- Configuración de rutas ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'datos_ventas.csv')
CLEAN_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'datos_ventas_limpios.csv')
ARIMA_PRED_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'arima_predictions.csv')
PROPHET_PRED_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'prophet_predictions.csv')

# --- Ejecución del pipeline completo ---
def run_pipeline():
    print("\n🚀 Iniciando pipeline completo de pronóstico de series temporales")

    # 1. Ingesta de datos crudos
    df_raw = load_raw_data(RAW_PATH)

    # 2. Limpieza de datos
    df_clean = clean_sales_data(df_raw)
    df_clean.to_csv(CLEAN_PATH, index=False)
    print(f"✅ Datos limpios guardados en {CLEAN_PATH}")

    # 3. ARIMA
    print("\n📈 Ejecutando modelo ARIMA...")
    df_clean_arima = df_clean.copy()
    df_clean_arima.set_index('fecha', inplace=True)
    train_a, test_a = arima_split(df_clean_arima)
    order = select_arima_order(train_a['ventas'])
    model_a = train_arima(train_a['ventas'], order)
    pred_a = forecast_arima(model_a, steps=len(test_a))
    rmse_a, mae_a, mape_a = evaluate_arima(test_a['ventas'], pred_a)
    test_a = test_a.copy()
    test_a['predicciones'] = pred_a.values
    test_a.to_csv(ARIMA_PRED_PATH)
    print(f"✅ ARIMA completado y predicciones guardadas en {ARIMA_PRED_PATH}")

    # 4. Prophet
    print("\n📈 Ejecutando modelo Prophet...")
    df_clean_prophet = load_for_prophet(CLEAN_PATH)
    train_p, test_p = prophet_split(df_clean_prophet)
    model_p = train_prophet(train_p)
    forecast_p = forecast_prophet(model_p, periods=len(test_p))
    pred_p = forecast_p[['ds', 'yhat']].tail(len(test_p)).set_index('ds')
    rmse_p, mae_p, mape_p = evaluate_prophet(test_p['y'], pred_p['yhat'])
    test_p = test_p.copy()
    test_p['predicciones'] = pred_p['yhat'].values
    test_p.to_csv(PROPHET_PRED_PATH, index=False)
    print(f"✅ Prophet completado y predicciones guardadas en {PROPHET_PRED_PATH}")

    # 5. Resumen de métricas
    print("\n📊 Resumen de métricas de modelos:")
    print(f"ARIMA   → RMSE: {rmse_a:.2f} | MAE: {mae_a:.2f} | MAPE: {mape_a:.2f}%")
    print(f"Prophet → RMSE: {rmse_p:.2f} | MAE: {mae_p:.2f} | MAPE: {mape_p:.2f}%")

if __name__ == "__main__":
    run_pipeline()