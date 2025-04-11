# Dockerfile

FROM python:3.11-slim 

# Directorio de trabajo
WORKDIR /app

# Copiar archivos necesarios
COPY . /app

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponer puerto de Streamlit
EXPOSE 8501

# Comando para ejecutar Streamlit
CMD ["streamlit", "run", "src/visualization/dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
