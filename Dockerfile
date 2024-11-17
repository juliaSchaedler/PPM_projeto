# Usa uma imagem base do Python
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos necessários para o contêiner
COPY requirements.txt .  
COPY . .  

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Comando para rodar o programa
CMD ["python", "main.py"]
