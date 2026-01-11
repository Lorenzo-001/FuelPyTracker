# 1. Usa un'immagine base di Python leggera (Debian Slim)
FROM python:3.11-slim

# 2. Evita che Python scriva file __pycache__ e bufferizzi l'output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Imposta la cartella di lavoro dentro il container virtuale
WORKDIR /app

# 4. Copia il file dei requisiti e installa le dipendenze
# Facciamo questo PRIMA di copiare il codice per sfruttare la cache di Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia tutto il resto del codice del progetto
COPY . .

# 6. Esponi la porta standard di Streamlit
EXPOSE 8501

# 7. Verifica che il container sia sano (Healthcheck)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 8. Comando di avvio dell'app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]