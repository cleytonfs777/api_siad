import asyncio
from fastapi import HTTPException,WebSocket, WebSocketDisconnect
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.WebSocketConnect import ConnectionManager
from app.db.models import ReseterNeed, UserModel
from app.depends import get_db_session, token_verifier
from app.auth_user import UserUseCases
from app.schemas import MessageUser, ResetRequest, User, UserLogin, ForgotPassword, Userreset
from uuid import uuid1
from decouple import config
from app.sender_email import send_email

manager = ConnectionManager()


user_router = APIRouter(prefix='/user')
reset_router = APIRouter(prefix='/reset')
admin_router = APIRouter(prefix='/admin', dependencies=[Depends(token_verifier)])

# Variáveis globais
IS_BUSY = False
lock = asyncio.Lock()
active_websockets = {}  # lista para armazenar conexões

@user_router.post('/register')
def user_register(
    user: User,
    db_session: Session = Depends(get_db_session),
):
    uc = UserUseCases(db_session=db_session)
    uc.user_register(user=user)
    return JSONResponse(
        content={'msg': 'success'},
        status_code=status.HTTP_201_CREATED
    )


@user_router.post('/login')
def user_login(
    request_form_user: OAuth2PasswordRequestForm = Depends(),
    db_session: Session = Depends(get_db_session),
):
    uc = UserUseCases(db_session=db_session)
    user = UserLogin(
        username=request_form_user.username,
        password=request_form_user.password
    )

    auth_data = uc.user_login(user=user)
    return JSONResponse(
        content=auth_data,
        status_code=status.HTTP_200_OK
    )
@user_router.post('forgot-password')
def forgot_password(
    request: ForgotPassword,
    db_session: Session = Depends(get_db_session),
    ):
    print(f"email: {request.email} username: {request.username}")
    # Retorna todos os registro do banco:
    all_users = db_session.query(UserModel).all()
    for user in all_users:
        print(user.email, user.username)
    # Verifica se existe o email e usuario na tabela users
    existing_user = db_session.query(UserModel).filter_by(email=request.email, username=request.username).first()
    if not existing_user:
        raise HTTPException(
            status_code=400,
            detail='Usuário ou email inválido'
        )
    # Cria código de reset e salva no banco de dados
    reset_code = str(uuid1())
    

    return reset_code


@reset_router.post('/register-reset')
async def register_reset_request(user: Userreset, db_session: Session = Depends(get_db_session)):
    global IS_BUSY, active_websockets

    # Verifica se já existe um pedido de reset
    existing_request = db_session.query(ReseterNeed).filter_by(username=user.username).first()
    if existing_request:
        raise HTTPException(status_code=400, detail='Pedido já em andamento.')

    websocket = active_websockets.get('token')
    if websocket and not IS_BUSY:
        IS_BUSY = True
        try:
            await websocket.send_json({"username": user.username, "email": user.email})
            return JSONResponse(content={"message": "Pedido de reset enviado e confirmado com sucesso. Enviaremos um email de confirmação"}, status_code=200)
        except Exception as e:
            print(f"Erro durante o envio/recepção: {e}")
    else:
        new_request = ReseterNeed(username=user.username, email=user.email)
        db_session.add(new_request)
        db_session.commit()
        return JSONResponse(content={"message": "Pedido de reset registrado. Aguarde a liberação."}, status_code=200)


# @admin_router.get('/request')
# def get_and_delete_request(user: UserModel = Depends(token_verifier), db_session: Session = Depends(get_db_session)):
#     # Verifica se o usuário é o administrador
#     print(user.username)
#     if user.username != "admincbmmg":
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Acesso negado - {user.username}")

#     # Busca o primeiro pedido de reset
#     reset_request = db_session.query(ReseterNeed).first()
#     if not reset_request:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum pedido encontrado")

#     # Prepara os dados para retorno
#     request_data = {"id": reset_request.id, "username": reset_request.username, "email": reset_request.email}

#     # Exclui o registro do banco de dados
#     db_session.delete(reset_request)
#     db_session.commit()

#     return request_data


@reset_router.post('/add-request')
def add_reset_request(user_message: MessageUser, db_session: Session = Depends(get_db_session)):
    # Verifica se o usuário é o administrador
    if user_message.token != config("SECRET_CODE"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    # Ao receber a msg e o email envia para o usuario
    if user_message.email and user_message.message:
        response = send_email(user_message.message, user_message.email)
        return response



@reset_router.websocket("/ws/resetkey")
async def websocket_resets(websocket: WebSocket, db_session: Session = Depends(get_db_session)):
    global active_websockets, IS_BUSY
    await websocket.accept()
    token = websocket.query_params.get("token")

    if config("SECRET_CODE") != token:
        await websocket.close(code=1000)
        return

    active_websockets["token"] = websocket

    # Processa imediatamente as requisições pendentes ao conectar
    await process_reset_requests(db_session, websocket)

    try:
        while True:
            message = await websocket.receive_text()
            print(f"Message received: {message}")
            IS_BUSY = False
            await process_reset_requests(db_session, websocket)
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        async with lock:
            IS_BUSY = False
            if token in active_websockets:
                del active_websockets[token]
        await websocket.close()


async def process_reset_requests(db_session, websocket):
    """ Processar e enviar solicitações de reset se disponíveis e quando não estiver ocupado. """
    global IS_BUSY, active_websockets  # Declarar como global se for modificar
    
    while not IS_BUSY:
        reset_request = db_session.query(ReseterNeed).first()
        if reset_request:
            print(f"Mandando requisição da funçao Websocket: {reset_request}")
            await websocket.send_json({"id": reset_request.id, "username": reset_request.username, "email": reset_request.email})
            IS_BUSY = True
            # Aguardar pela confirmação de processamento do cliente
            response = await websocket.receive_text()
            print(f"Resposta do cliente: {response}")
            if response == "OK":
                db_session.delete(reset_request)
                db_session.commit()
            IS_BUSY = False  # Marcar como não ocupado após o processamento
        else:
            break