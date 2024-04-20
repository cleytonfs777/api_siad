import asyncio
from fastapi import HTTPException,WebSocket, WebSocketDisconnect
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.models import ReseterNeed, UserModel
from app.depends import get_db_session, token_verifier
from app.auth_user import UserUseCases
from app.schemas import ResetRequest, User, UserLogin, ForgotPassword, Userreset
from uuid import uuid1

user_router = APIRouter(prefix='/user')
reset_router = APIRouter(prefix='/reset')
admin_router = APIRouter(prefix='/admin', dependencies=[Depends(token_verifier)])

# Variáveis globais
IS_BUSY = False
lock = asyncio.Lock()
active_websocket = None

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


# Assume-se que lock e IS_BUSY foram definidos anteriormente
@reset_router.post('/register-reset')
async def register_reset_request(user: Userreset, db_session: Session = Depends(get_db_session)):
    global IS_BUSY, active_websocket
    async with lock:
        # Verifica se já existe um pedido de reset para esse usuário
        existing_request = db_session.query(ReseterNeed).filter_by(username=user.username).first()
        if existing_request:
            raise HTTPException(
                status_code=400,
                detail='Favor aguarde. Há um pedido em andamento...'
            )

        # Se o WebSocket estiver ativo e não estiver ocupado, envia diretamente
        if active_websocket and not IS_BUSY:
            IS_BUSY = True
            try:
                await active_websocket.send_json({"username": user.username})
                response = await active_websocket.receive_text()
                if response == "OK":
                    # Se a resposta for "OK", não salva no banco pois já foi processado
                    return {"message": "Pedido de reset registrado com sucesso. Aguarde alguns minutos para usar a nova senha"}
                # Se a resposta não for "OK", procede para salvar no banco abaixo
            finally:
                IS_BUSY = False
        else:
            # Cria e salva no banco apenas se o WebSocket não estiver disponível ou estiver ocupado
            new_request = ReseterNeed(username=user.username)
            db_session.add(new_request)
            db_session.commit()
            return {"message": "Pedido de reset registrado com sucesso. Aguarde alguns minutos para usar a nova senha"}


# @reset_router.post('/register-reset')
# def register_reset_request(user: Userreset, db_session: Session = Depends(get_db_session)):
#     # Verifica se já existe um pedido de reset para esse número
#     existing_request = db_session.query(ReseterNeed).filter_by(username=user.username).first()
#     if existing_request:
#         # Levanta a exceção corretamente
#         raise HTTPException(
#             status_code=400,
#             detail='Favor aguarde. Há um pedido em andamento...'
# )

#     # Se não existir, cria um novo pedido de reset
#     new_request = ReseterNeed(username=user.username)
#     db_session.add(new_request)
#     db_session.commit()

#     return {"message": "Pedido de reset registrado com sucesso. Aguarde alguns minutos para usar a nova senha"}


@admin_router.get('/request')
def get_and_delete_request(user: UserModel = Depends(token_verifier), db_session: Session = Depends(get_db_session)):
    # Verifica se o usuário é o administrador
    print(user.username)
    if user.username != "admincbmmg":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Acesso negado - {user.username}")

    # Busca o primeiro pedido de reset
    reset_request = db_session.query(ReseterNeed).first()
    if not reset_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum pedido encontrado")

    # Prepara os dados para retorno
    request_data = {"id": reset_request.id, "username": reset_request.username}

    # Exclui o registro do banco de dados
    db_session.delete(reset_request)
    db_session.commit()

    return request_data


@admin_router.post('/add-request')
def add_reset_request(request_data: ResetRequest, user: UserModel = Depends(token_verifier), db_session: Session = Depends(get_db_session)):
    # Verifica se o usuário é o administrador
    if user.username != "admincbmmg":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    # Cria um novo registro com o número enviado
    new_request = ReseterNeed(username=request_data.username)
    db_session.add(new_request)
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"message": "Pedido de reset adicionado com sucesso.", "username": request_data.username}


@admin_router.websocket("/ws/resets")
async def websocket_resets(websocket: WebSocket, user: UserModel = Depends(token_verifier), db_session: Session = Depends(get_db_session)):
    global IS_BUSY
    await websocket.accept()
    if user.username != "admincbmmg":
        await websocket.close(code=1000)
        return

    try:
        while True:
            reset_request = None
            async with lock:
                if not IS_BUSY:
                    reset_request = db_session.query(ReseterNeed).first()
                    if reset_request:
                        await websocket.send_json({"id": reset_request.id, "username": reset_request.username})
                        IS_BUSY = True

            if reset_request:
                response = await websocket.receive_text()
                if response == "OK":
                    db_session.delete(reset_request)
                    db_session.commit()

                async with lock:
                    IS_BUSY = False  # Marca como não ocupado após receber qualquer resposta
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        async with lock:
            IS_BUSY = False
        await websocket.close()