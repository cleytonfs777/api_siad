from fastapi import FastAPI
from app.routes import user_router, reset_router, admin_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Lista de origens permitidas
origins = [
    "https://hml.intranet.bombeiros.mg.gov.br",
    "http://localhost",
    "http://localhost:8080",  # Inclua outras portas ou origens conforme necessário
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Lista de origens que podem fazer requisições
    allow_credentials=True,  # Permite cookies de origens cruzadas
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

@app.get("/")
def health_check():
    return "Ok, it's alive!"

app.include_router(user_router)
app.include_router(reset_router)
app.include_router(admin_router)