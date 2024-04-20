# Usar uma imagem base oficial do Python
FROM python:3.9

# Definir o diretório de trabalho no container
WORKDIR /code

# Copiar os arquivos de dependências e instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copiar os arquivos da aplicação para o container
COPY ./app /code/app
COPY alembic.ini .
COPY migrations /code/migrations

# Executar migrações antes de iniciar a aplicação
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
