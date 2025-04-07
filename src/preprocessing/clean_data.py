# clean_data.py
import pandas as pd

def clean_and_transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y transforma los datos del DataFrame original.

    Parameters:
    df (pd.DataFrame): DataFrame con datos crudos.

    Returns:
    pd.DataFrame: DataFrame limpio y transformado.
    """
    # Transformar columna de fecha a datetime
    df['fecha'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d', errors='coerce')

    # Validar conversión correcta
    if df['fecha'].isnull().any():
        raise ValueError("Se encontraron fechas no válidas tras la conversión.")

    # Ordenar por fecha
    df.sort_values('fecha', inplace=True)

    # Manejar valores faltantes (si existieran)
    if df['ventas'].isnull().any():
        # Aquí optamos por rellenar con la media, pero puedes cambiar la estrategia
        df['ventas'].fillna(df['ventas'].mean(), inplace=True)
        print("⚠️ Se detectaron valores nulos en 'ventas'. Se rellenaron con la media.")

    # Restablecer índices tras ordenar
    df.reset_index(drop=True, inplace=True)

    print("✅ Datos limpios y transformados correctamente.")
    print(f"Rango de fechas desde {df['fecha'].min()} hasta {df['fecha'].max()}")

    return df

# Ejemplo de ejecución local (para prueba rápida)
if __name__ == "__main__":
    from src.ingestion.load_data import load_raw_data

    ruta_csv = "data/raw/datos_ventas.csv"
    df_raw = load_raw_data(ruta_csv)
    df_clean = clean_and_transform_data(df_raw)
