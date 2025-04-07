# load_data.py
import pandas as pd
import os

def load_raw_data(file_path: str) -> pd.DataFrame:
    """
    Carga los datos en formato CSV desde la ubicación especificada.

    Parameters:
    file_path (str): Ruta del archivo CSV a cargar.

    Returns:
    pd.DataFrame: DataFrame con los datos cargados.
    """
    # Verifica que el archivo exista en la ruta proporcionada
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe. Verifica la ruta.")

    # Cargar datos con Pandas
    df = pd.read_csv(file_path)

    # Mostrar información básica para validar la carga correcta
    print(f"✅ Datos cargados correctamente desde {file_path}.")
    print(f"Número de filas y columnas: {df.shape}")
    print("Primeras 5 filas:")
    print(df.head())

    return df

# Ejemplo de ejecución local (para prueba rápida)
if __name__ == "__main__":
    ruta_csv = "data/raw/datos_ventas.csv"  # Ajustar según tu ubicación exacta
    df = load_raw_data(ruta_csv)
