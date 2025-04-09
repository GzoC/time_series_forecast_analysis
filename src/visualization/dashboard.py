# src/visualization/dashboard.py

import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# --- Configuración inicial de la app ---
st.set_page_config(page_title="Forecast Dashboard", layout="centered")
st.title("📊 Dashboard de Pronóstico de Series Temporales")

# --- Función para cargar los datos de predicciones ---
def load_predictions(model: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '..', '..', 'data', 'processed', f'{model}_predictions.csv')
    df = pd.read_csv(file_path)
    df['fecha'] = pd.to_datetime(df['fecha'] if 'fecha' in df.columns else df['ds'])
    return df

# --- Selección de modelo ---
model_option = st.selectbox("Selecciona el modelo para visualizar:", ("arima", "prophet"))
df = load_predictions(model_option)

# --- Mostrar tabla de predicciones ---
st.subheader("Vista de Datos de Predicción")
st.dataframe(df.tail(30), use_container_width=True)

# --- Gráfico de predicciones ---
st.subheader("Gráfico de Predicción vs Real")
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df['fecha'], df['ventas' if 'ventas' in df.columns else 'y'], label='Real', marker='o')
ax.plot(df['fecha'], df['predicciones'], label='Predicción', marker='x')
ax.set_xlabel("Fecha")
ax.set_ylabel("Ventas")
ax.set_title(f"Predicciones - Modelo {model_option.upper()}")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# --- Métricas básicas ---
df['error_abs'] = abs(df['predicciones'] - (df['ventas'] if 'ventas' in df.columns else df['y']))
df['error_pct'] = df['error_abs'] / (df['ventas'] if 'ventas' in df.columns else df['y']) * 100

rmse = (df['error_abs']**2).mean()**0.5
mae = df['error_abs'].mean()
mape = df['error_pct'].mean()

st.subheader("📈 Métricas del Modelo")
st.markdown(f"**RMSE:** {rmse:.2f}")
st.markdown(f"**MAE:** {mae:.2f}")
st.markdown(f"**MAPE:** {mape:.2f}%")
