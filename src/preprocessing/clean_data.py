# src/preprocessing/clean_data.py

import pandas as pd
import numpy as np

def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y prepara los datos de ventas para análisis y modelado.

    Args:
        df (pd.DataFrame): DataFrame con datos brutos ('fecha', 'ventas').

    Returns:
        pd.DataFrame: DataFrame limpio y transformado.
    """

    # --- Manejo de valores nulos ---
    if df['ventas'].isnull().sum() > 0:
        # Interpolación lineal para rellenar valores nulos
        df['ventas'] = df['ventas'].interpolate(method='linear')
        print("⚠️ Se encontraron valores nulos. Se realizó interpolación lineal para rellenarlos.")
    else:
        print("✅ No se encontraron valores nulos.")

    # --- Detección de outliers mediante método IQR ---
    Q1 = df['ventas'].quantile(0.25)  # Primer cuartil
    Q3 = df['ventas'].quantile(0.75)  # Tercer cuartil
    IQR = Q3 - Q1  # Rango Intercuartílico
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Identificación de outliers
    outliers = df[(df['ventas'] < lower_bound) | (df['ventas'] > upper_bound)]
    num_outliers = len(outliers)

    if num_outliers > 0:
        print(f"⚠️ Se detectaron {num_outliers} valores atípicos. Aplicando corrección mediante interpolación.")
        # Reemplazo de outliers con NaN temporalmente
        df.loc[(df['ventas'] < lower_bound) | (df['ventas'] > upper_bound), 'ventas'] = np.nan
        # Interpolamos nuevamente para corregir estos valores
        df['ventas'] = df['ventas'].interpolate(method='linear')
    else:
        print("✅ No se detectaron valores atípicos.")

    # --- Validar y ordenar fechas ---
    # Aseguramos que la columna 'fecha' sea tipo datetime (fecha)
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Ordenamos cronológicamente
    df = df.sort_values(by='fecha').reset_index(drop=True)
    print("✅ Fechas validadas y ordenadas cronológicamente.")

    # Retornamos el DataFrame limpio
    return df

# Ejecución independiente para prueba rápida
if __name__ == "__main__":
    import os

    # Ubicación relativa del archivo CSV de datos en bruto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_raw_path = os.path.join(base_dir, '..', '..', 'data', 'raw', 'datos_ventas.csv')
