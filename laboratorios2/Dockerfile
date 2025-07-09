# Imagen reducida de Python 3.10
FROM python:3.10-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo el archivo requirements.txt
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Exponer el puerto en el que Uvicorn (FastAPI) escuchará
EXPOSE 8000

# Comando para ejecutar la aplicación cuando el contenedor se inicie
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]