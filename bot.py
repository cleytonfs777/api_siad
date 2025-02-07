import asyncio
import websockets
from decouple import config, UndefinedValueError
import requests

url_email = "http://fastapi:8000/reset/add-request"
headers = {
    'Content-Type': 'application/json'
}


async def cadastro_militar(username):
    await asyncio.sleep(5)  # Simula a execução do robô
    print(f"Esse é meu Username: {username}")
    return {
        "status": "OK",
        "message": "Reset de senha realizado com sucesso. Entre com a senha padrão 'snhrcf' e redefina. Em caso de dúvidas ligue para (31)312-3456"
    }


async def connect_to_websocket():
    try:
        secret_code = config("SECRETCODE")
    except UndefinedValueError as e:
        print(f"Error: {e}")
        return

    uri = f"ws://fastapi:8000/reset/ws/resetkey?token={secret_code}"

    while True:
        try:
            print("Tentando conectar ao websocket...")
            async with websockets.connect(uri) as websocket:
                print("Conexão websocket realizada com sucesso!")
                try:
                    while True:
                        message = await websocket.recv()
                        print(f"Received message: {message}")
                        message = eval(message)
                        response_mail = await cadastro_militar(message["username"])
                        response_body = {
                            "token": secret_code,
                            "email": message["email"],
                            "message": response_mail["message"]
                        }
                        print(f"""
                        Email: {message["email"]}
                        Message: {response_mail["message"]}
                        """)
                        requests.post(
                            url_email, json=response_body, headers=headers)
                        await websocket.send(response_mail["status"])
                        print("Enviada a mensagem:", response_mail["status"])
                except websockets.exceptions.ConnectionClosed as e:
                    print(
                        f"Connection closed unexpectedly: {e}. Reconnecting...")
                    continue
        except Exception as e:
            print(f"Failed to connect: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)


def main():
    asyncio.run(connect_to_websocket())


if __name__ == "__main__":
    main()
