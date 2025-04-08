# src/modeling/prophet_model.py

import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_error
import os
import warnings
warnings.filterwarnings('ignore')  # Ignorar advertencias no críticas

# --- Cargar datos limpios y formatearlos para Prophet ---

def load_clean_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.rename(columns={'fecha': 'ds', 'ventas': 'y'}, inplace=True)
    df['ds'] = pd.to_datetime(df['ds'])
    return df

# --- División en entrenamiento y validación ---

def train_test_split(df: pd.DataFrame, test_size: int = 30):
    train, test = df[:-test_size], df[-test_size:]
    return train, test

# --- Entrenar modelo Prophet ---

def train_prophet(train: pd.DataFrame):
    model = Prophet()
    model.fit(train)
    return model

# --- Pronosticar con Prophet ---

def forecast_prophet(model, periods: int):
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
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

    # Cargar y preparar datos limpios
    df = load_clean_data(data_path)
    train, test = train_test_split(df)

    # Entrenar modelo Prophet
    model = train_prophet(train)

    # Pronosticar
    forecast = forecast_prophet(model, periods=len(test))
    predictions = forecast[['ds', 'yhat']].tail(len(test)).set_index('ds')

    # Evaluar modelo
    rmse, mae, mape = evaluate_model(test['y'], predictions['yhat'])

    # Mostrar métricas
    print('\n✅ Prophet - Métricas del modelo:')
    print(f'RMSE: {rmse:.2f}')
    print(f'MAE: {mae:.2f}')
    print(f'MAPE: {mape:.2f}%')

    # Guardar predicciones
    predictions_df = test.copy()
    predictions_df['predicciones'] = predictions['yhat'].values

    predictions_path = os.path.join(base_dir, '..', '..', 'data', 'processed', 'prophet_predictions.csv')
    predictions_df.to_csv(predictions_path, index=False)

    print(f'✅ Predicciones guardadas en {predictions_path}')
