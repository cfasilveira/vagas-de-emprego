# Usa a imagem oficial leve
FROM python:3.12-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala o uv dentro do container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copia apenas os arquivos de dependências primeiro (Cache optimization)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# Copia o restante do código
COPY . .

ENV PYTHONPATH=/app

# Expõe a porta do Streamlit
EXPOSE 8501

# COMANDO CORRIGIDO: Aponta para o main.py da raiz
CMD ["uv", "run", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
