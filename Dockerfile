# Usa uma imagem base oficial do Python 3.10
FROM python:3.10-slim

# Define o diretÃƒÆ’Ã‚Â³rio de trabalho no container
WORKDIR /app

# Copia o arquivo requirements.txt para o diretÃƒÆ’Ã‚Â³rio de trabalho
COPY requirements.txt .

# Instala as dependÃƒÆ’Ã‚Âªncias do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o conteÃƒÆ’Ã‚Âºdo do diretÃƒÆ’Ã‚Â³rio atual para o diretÃƒÆ’Ã‚Â³rio de trabalho no container
COPY . .

# Instala o pacote python-dotenv para carregar as variÃƒÆ’Ã‚Â¡veis de ambiente do arquivo .env
RUN pip install python-dotenv

# Define o comando padrÃƒÆ’Ã‚Â£o para rodar a aplicaÃƒÆ’Ã‚Â§ÃƒÆ’Ã‚Â£o quando o container iniciar
CMD ["python", "-u", "main.py"]