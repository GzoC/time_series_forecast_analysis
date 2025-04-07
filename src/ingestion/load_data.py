# src/ingestion/load_data.py

import pandas as pd
import os

def load_raw_data(file_path: str) -> pd.DataFrame:
    """
    Función para cargar datos brutos desde un archivo CSV.

    Args:
        file_path (str): Ruta completa hacia el archivo CSV.

    Returns:
        pd.DataFrame: DataFrame con los datos cargados.
    """
    # Validamos que la ruta del archivo exista
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo no se encuentra en: {file_path}")

    # Leemos el archivo CSV usando pandas
    df = pd.read_csv(file_path, parse_dates=['fecha'])

    # Validamos las columnas mínimas necesarias
    expected_columns = {'fecha', 'ventas'} # Definimos las columnas esperadas
    if not expected_columns.issubset(df.columns):   # Verificamos si faltan columnas
        # Si faltan columnas, generamos un error con los nombres de las columnas faltantes
        missing_cols = expected_columns - set(df.columns)
        raise ValueError(f"Faltan columnas necesarias en el archivo CSV: {missing_cols}")

    # Ordenamos los datos por fecha
    df = df.sort_values(by='fecha').reset_index(drop=True)

    print(f"✅ Datos cargados exitosamente desde {file_path}")
    print(f"Total de registros cargados: {len(df)}")
    print("Vista previa de los datos:")
    print(df.head())

    return df

# Ejecución independiente para prueba rápida
if __name__ == "__main__":
    # Ruta relativa desde la ubicación actual del script hacia los datos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', '..', 'data', 'raw', 'datos_ventas.csv')

    # Cargamos los datos
    df_ventas = load_raw_data(csv_path)
