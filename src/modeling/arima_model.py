# src/modeling/arima_model.py

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os
import warnings
warnings.filterwarnings('ignore')  # Ignorar advertencias no críticas

# --- Cargar datos limpios ---

def load_clean_data(path: str) -> pd.DataFrame: 
    df = pd.read_csv(path, parse_dates=['fecha']) 
    df.set_index('fecha', inplace=True) 
    return df

# --- División en entrenamiento y validación ---

def train_test_split(df: pd.DataFrame, test_size: int = 30):
    train, test = df[:-test_size], df[-test_size:]
    return train, test

# --- Selección automática de parámetros ARIMA (p,d,q) ---

def select_arima_order(train: pd.Series):
    # Para simplificar, usamos parámetros fijos comunes
    best_order = (5,1,0)  # (p,d,q) - valores razonables iniciales
    return best_order

# --- Entrenar y pronosticar con ARIMA ---

def train_arima(train: pd.Series, order: tuple): 
    model = ARIMA(train, order=order)
    model_fit = model.fit()
    return model_fit

# --- Pronosticar valores ---

def forecast_arima(model_fit, steps: int):
    forecast = model_fit.forecast(steps=steps)
    return forecast

# --- Evaluar modelo ---

def evaluate_model(actual, predicted):
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mae = mean_absolute_error(actual, predicted)
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100
    return rmse, mae, mape

# --- Main ---

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, '..', '..', 'data', 'processed', 'datos_ventas_limpios.csv')

    # Cargar datos limpios
    df = load_clean_data(data_path)
    train, test = train_test_split(df)

    # Seleccionar orden ARIMA
    order = select_arima_order(train['ventas'])

    # Entrenar modelo ARIMA
    model_fit = train_arima(train['ventas'], order)

    # Pronosticar
    predictions = forecast_arima(model_fit, steps=len(test))

    # Evaluar modelo
    rmse, mae, mape = evaluate_model(test['ventas'], predictions)

    # Mostrar métricas
    print(f'\n✅ ARIMA({order}) - Métricas del modelo:')
    print(f'RMSE: {rmse:.2f}')
    print(f'MAE: {mae:.2f}')
    print(f'MAPE: {mape:.2f}%')

    # Guardar predicciones
    predictions_df = test.copy()
    predictions_df['predicciones'] = predictions.values

    predictions_path = os.path.join(base_dir, '..', '..', 'data', 'processed', 'arima_predictions.csv')
    predictions_df.to_csv(predictions_path)

    print(f'✅ Predicciones guardadas en {predictions_path}')
