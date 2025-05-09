# Usa imagem oficial do Python
FROM python:3.12-slim

# Evita prompts durante a instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instala ffmpeg e dependências
RUN apt-get update && \
    apt-get install -y ffmpeg gcc libffi-dev libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Cria diretório para o bot
WORKDIR /app

# Copia os arquivos do seu projeto para dentro do contêiner
COPY . .

# Instala as dependências do projeto
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe a porta (não obrigatório para bots do Discord, mas bom para Railway)
EXPOSE 8080

# Comando para iniciar o bot
CMD ["python", "main.py"]
