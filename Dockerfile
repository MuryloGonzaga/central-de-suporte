# Imagem base oficial do Python Slim (leve e segura)
FROM python:3.11-slim

# Evita criação de arquivos .pyc e permite que os logs saiam imediatamente no console
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Expõe a porta configurada
EXPOSE 8000

# Healthcheck do container
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

# Comando padrão para iniciar a aplicação
CMD ["python", "run.py"]

