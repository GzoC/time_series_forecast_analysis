# src/modeling/model_evaluation.py

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os
import matplotlib.pyplot as plt

# --- Función para calcular métricas ---
def evaluate_metrics(actual, predicted):
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mae = mean_absolute_error(actual, predicted)
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    return rmse, mae, mape

# --- Cargar predicciones y evaluar ---
def load_and_evaluate(model_name: str, file_path: str):
    df = pd.read_csv(file_path)
    actual = df['ventas'] if 'ventas' in df.columns else df['y']
    predicted = df['predicciones']

    rmse, mae, mape = evaluate_metrics(actual, predicted)

    print(f"\n📊 Resultados para {model_name}:")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAE: {mae:.2f}")
    print(f"MAPE: {mape:.2f}%")

    return df, rmse, mae, mape

# --- Visualizar comparaciones ---
def plot_comparison(df, title):
    plt.figure(figsize=(10, 5))
    plt.plot(df['fecha'] if 'fecha' in df.columns else df['ds'], df['ventas' if 'ventas' in df.columns else 'y'], label='Real')
    plt.plot(df['fecha'] if 'fecha' in df.columns else df['ds'], df['predicciones'], label='Predicción')
    plt.title(title)
    plt.xlabel('Fecha')
    plt.ylabel('Ventas')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# --- Main ---
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Rutas a archivos de predicción
    arima_path = os.path.join(base_dir, '..', '..', 'data', 'processed', 'arima_predictions.csv')
    prophet_path = os.path.join(base_dir, '..', '..', 'data', 'processed', 'prophet_predictions.csv')

    # Evaluar y visualizar ARIMA
    arima_df, arima_rmse, arima_mae, arima_mape = load_and_evaluate("ARIMA", arima_path)
    plot_comparison(arima_df, "ARIMA: Real vs Predicción")

    # Evaluar y visualizar Prophet
    prophet_df, prophet_rmse, prophet_mae, prophet_mape = load_and_evaluate("Prophet", prophet_path)
    plot_comparison(prophet_df, "Prophet: Real vs Predicción")

    # Comparación final en consola
    print("\n📌 Comparación final de modelos:")
    print(f"ARIMA   → RMSE: {arima_rmse:.2f} | MAE: {arima_mae:.2f} | MAPE: {arima_mape:.2f}%")
    print(f"Prophet → RMSE: {prophet_rmse:.2f} | MAE: {prophet_mae:.2f} | MAPE: {prophet_mape:.2f}%")
