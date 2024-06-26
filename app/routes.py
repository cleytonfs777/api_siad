import asyncio
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.WebSocketConnect import ConnectionManager
from app.db.models import ReseterNeed, UserModel
from app.depends import get_db_session
from app.schemas import MessageUser, ResetRequest, User, UserLogin, ForgotPassword, Userreset
from uuid import uuid1
from decouple import config
from app.sender_email import send_email

manager = ConnectionManager()

user_router = APIRouter(prefix='/user')
reset_router = APIRouter(prefix='/reset')

IS_BUSY = False
active_websockets = {}


@reset_router.post('/register-reset')
async def register_reset_request(user: Userreset, db_session: Session = Depends(get_db_session)):
    global IS_BUSY, active_websockets

    existing_request = db_session.query(
        ReseterNeed).filter_by(username=user.username).first()
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
            IS_BUSY = False
            new_request = ReseterNeed(username=user.username, email=user.email)
            db_session.add(new_request)
            db_session.commit()
            return JSONResponse(content={"message": "Pedido de reset registrado. Aguarde a liberação."}, status_code=200)
    else:
        new_request = ReseterNeed(username=user.username, email=user.email)
        db_session.add(new_request)
        db_session.commit()
        return JSONResponse(content={"message": "Pedido de reset registrado. Aguarde a liberação."}, status_code=200)


@reset_router.post('/add-request')
def add_reset_request(user_message: MessageUser, db_session: Session = Depends(get_db_session)):
    if user_message.token != config("SECRETCODE"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
    if user_message.email and user_message.message:
        response = send_email(user_message.message, user_message.email)
        return response


@reset_router.websocket("/ws/resetkey")
async def websocket_resets(websocket: WebSocket, db_session: Session = Depends(get_db_session)):
    global active_websockets, IS_BUSY
    await websocket.accept()
    token = websocket.query_params.get("token")

    if config("SECRETCODE") != token:
        await websocket.close(code=1000)
        return

    active_websockets["token"] = websocket

    print("WebSocket conectado, processando requisições pendentes...")
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
        IS_BUSY = False
        if token in active_websockets:
            del active_websockets[token]
        await websocket.close()


async def process_reset_requests(db_session, websocket):
    global IS_BUSY, active_websockets
    while not IS_BUSY:
        reset_request = db_session.query(ReseterNeed).first()
        if reset_request:
            print(f"Mandando requisição da função Websocket: {reset_request}")
            try:
                await websocket.send_json({"id": reset_request.id, "username": reset_request.username, "email": reset_request.email})
                IS_BUSY = True
                response = await websocket.receive_text()
                print(f"Resposta do cliente: {response}")
                if response == "OK":
                    db_session.delete(reset_request)
                    db_session.commit()
                IS_BUSY = False
            except Exception as e:
                print(f"Erro durante o envio/recepção: {e}")
                IS_BUSY = False
                break
        else:
            print("Nenhuma requisição pendente no banco de dados.")
            break
