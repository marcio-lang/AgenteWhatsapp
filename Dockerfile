# Imagem oficial e estável do Python 3.13 (versão Slim para menor tamanho e maior segurança)
FROM python:3.13-slim

# Evita que o Python grave arquivos bytecode (.pyc) no container
ENV PYTHONDONTWRITEBYTECODE=1

# Evita o buffer da saída do console pelo Python (logs em tempo real)
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho no container
WORKDIR /app

# Instala dependências básicas de sistema (se necessário)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependência primeiro para aproveitar o cache do Docker
COPY requirements.txt /app/

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código-fonte para o container
COPY . /app/

# Cria o diretório de ofertas se ele não existir
RUN mkdir -p /app/ofertas

# Expõe a porta utilizada pelo servidor web Flask
EXPOSE 3000

# O comando padrão pode ser sobrescrito pelo docker-compose.yml
CMD ["python", "execution/webhook_server.py"]
