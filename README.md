
# Automação de Restauração de Senhas no Sistema SIAD RMBH

Esta aplicação automatiza a restauração de senhas no sistema interno do Corpo de Bombeiros chamado SIAD. A aplicação utiliza um cliente WebSocket para se comunicar com o servidor FastAPI e um banco de dados PostgreSQL para armazenar as solicitações de restauração de senha.

## Índice

- [Descrição](#descrição)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Descrição

Este projeto visa automatizar o processo de restauração de senhas para usuários do sistema SIAD. A aplicação permite que os usuários enviem solicitações de restauração de senha, que são processadas automaticamente por um cliente WebSocket conectado a um servidor FastAPI.

## Instalação

### Pré-requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Passos para Instalação

1. Clone o repositório:

    ```sh
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

    ```env
    POSTGRES_USER=seu_usuario
    POSTGRES_PASSWORD=sua_senha
    POSTGRES_DB=seu_banco_de_dados
    DB_URL="postgresql+psycopg2://seu_usuario:sua_senha@postgresql/siad"
    SECRET_KEY=sua_chave_secreta
    ALGORITHM=HS256
    PASSAP=sua_senha_passap
    USERPASSAR=seu_usuario_passar
    SECRETCODE=seu_codigo_secreto
    EMAILAPP=seu_email@gmail.com
    SENHAAPP=sua_senha_email
    ```

3. Construa e inicie os contêineres:

    ```sh
    docker-compose up -d --build
    ```

## Configuração

A configuração da aplicação é gerenciada através do arquivo `.env`. Certifique-se de preencher todas as variáveis corretamente antes de iniciar os contêineres.

### Exemplo de Arquivo `.env`

```env
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=seu_banco_de_dados
DB_URL="postgresql+psycopg2://seu_usuario:sua_senha@postgresql/siad"
SECRET_KEY=sua_chave_secreta
ALGORITHM=HS256
PASSAP=sua_senha_passap
USERPASSAR=seu_usuario_passar
SECRETCODE=seu_codigo_secreto
EMAILAPP=seu_email@gmail.com
SENHAAPP=sua_senha_email

## Uso

Certifique-se de que os contêineres estão rodando:


docker-compose ps

A aplicação FastAPI estará disponível em http://localhost:8000.

Para interagir com o sistema, utilize a documentação interativa do Swagger disponível em http://localhost:8000/docs.

As solicitações de restauração de senha são processadas automaticamente pelo cliente WebSocket.

## Tecnologias Utilizadas
Python: Linguagem de programação principal.
FastAPI: Framework para construção da API.
PostgreSQL: Banco de dados para armazenamento de solicitações.
Docker: Contêinerização da aplicação.
Docker Compose: Orquestração dos contêineres.
WebSockets: Comunicação em tempo real para processamento das solicitações.

Estrutura do Projeto

.
├── Dockerfile
├── Dockerfile.websocket
├── docker-compose.yml
├── .env
├── requirements.txt
├── app
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── depends.py
│   ├── sender_email.py
│   └── WebSocketConnect.py
├── bot.py
└── setup_and_run.sh

Dockerfile: Configuração do contêiner FastAPI.
Dockerfile.websocket: Configuração do contêiner WebSocket.
docker-compose.yml: Orquestração dos contêineres.
.env: Variáveis de ambiente.
requirements.txt: Dependências do projeto.
app/: Diretório contendo os módulos da aplicação FastAPI.
bot.py: Script para o cliente WebSocket.
setup_and_run.sh: Script para configurar e rodar a aplicação localmente.
Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e pull requests.

Licença
Este projeto está licenciado sob a MIT License.

### Instruções Adicionais

- Substitua os valores de exemplo no arquivo `.env` com os valores reais.
- Verifique se todos os caminhos e nomes de arquivos estão corretos.
- Adapte qualquer seção conforme necessário para seu projeto específico.

### Finalizando

Esse `README.md` deve fornecer uma visão completa e clara da sua aplicação, desde a instalação até a execução. Certifique-se de revisar e ajustar conforme necessário para refletir com precisão seu projeto.





