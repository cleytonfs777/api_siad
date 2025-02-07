import os
import json
import asyncio
import websockets
import requests
import pyautogui
import pyperclip
import subprocess
from time import sleep
from dotenv import load_dotenv
from utils_sistema import inicia_sistema, kill_processes_by_name

load_dotenv()  # take environment variables from .env.

url_email = os.getenv('URL_EMAIL')

headers = {'Content-Type': 'application/json'}

SISTEMA = os.getenv('SYSTEM')

# Envia email atraves da API


def get_api_key(num_api):
    return f"S{num_api[:-1]}"


def send_key_press(keys, delay=0.1):
    pyautogui.typewrite(keys)
    sleep(delay)


def get_screen(message, target):
    return target in message


def initialize_main():
    try:
        inicia_sistema()
        sleep(1)
        pyautogui.press('enter')
        for _ in range(9):
            send_key_press("\t")
        send_key_press("X\n")
        for _ in range(2):
            send_key_press("\t")
        send_key_press("X\n")
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False


def set_user(user_target):
    send_key_press(user_target + "\n")
    sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')
    sleep(0.5)
    mensagem2 = pyperclip.paste()

    if get_screen(mensagem2, "LIBERADO :"):
        return {"status": "OK", "message": "Reset de senha realizado com sucesso. Entre com a senha padrão 'snhrcf' e redefina."}
    else:
        return {"status": "ERROR", "message": "Usuário não cadastrado no sistema. Entre em contato com sua unidade"}


def new_military_registration_full(nummaster):
    if not nummaster.isdigit():
        print("Não tem número válido...")
        return

    numero = get_api_key(nummaster)
    if not initialize_main():
        return

    resultfinal = set_user(numero)
    print(f"Numero do usuario {numero}...")
    print(resultfinal["message"])

    # Fecha o sistema para evitar erros
    kill_processes_by_name("w3270")

    
    return resultfinal


async def connect_to_websocket():
    secret_code = os.getenv("SECRETCODE")
    uri = f"wss://apisiad-production.up.railway.app/reset/ws/resetkey?token={secret_code}"

    async with websockets.connect(uri) as websocket:
        print(f"Connecting to {uri}...")

        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received message: {data['email']}")
            response_mail = new_military_registration_full(data['username'])

            response_body = {
                "token": secret_code,
                "email": data['email'],
                "message": response_mail["message"]
            }

            requests.post(url_email, headers=headers,
                          data=json.dumps(response_body))
            await websocket.send(response_mail["status"])
            print(f"Sent message: {response_mail['status']}")

if __name__ == "__main__":
    # asyncio.run(connect_to_websocket())
    response_mail = new_military_registration_full('1730035')
    sleep(1)
    response_mail = new_military_registration_full('0020123')
    print("O resultado final é:")
    print(response_mail)
    # initialize_main()
