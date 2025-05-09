# Usa a imagem base do Python
FROM python:3.12-slim

# Instalação do ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Define o diretório de trabalho
WORKDIR /app

# Copia todos os arquivos do projeto para o diretório de trabalho no container
COPY . /app

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para rodar o bot
CMD ["python", "main.py"]
