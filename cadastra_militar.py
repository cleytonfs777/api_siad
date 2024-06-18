import os
import time
import json
import asyncio
import websockets
import requests
import pyautogui
import pyperclip
from decouple import config
import subprocess
from time import sleep

# Carregar variáveis de ambiente de um arquivo .env


url_email = "https://apisiad-production.up.railway.app/reset/add-request"
headers = {'Content-Type': 'application/json'}


def open_program():
    program_path = r"C:\Program Files (x86)\pw3270\pw3270.exe"
    subprocess.Popen([program_path])
    # Esperar um tempo para garantir que o programa tenha iniciado
    time.sleep(2)


def get_api_key(num_api):
    return f"S{num_api[:-1]}"


def send_key_press(keys, delay=0.1):
    pyautogui.typewrite(keys)
    time.sleep(delay)


def get_login(message, target):
    return target in message


def initialize_main():
    open_program()
    send_key_press("cbmmg")
    send_key_press("\t")
    send_key_press(config('MYNUMBER'))
    send_key_press("\t")
    send_key_press(config('MYPASS'))
    send_key_press("\n")

    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')
    mensagem1 = pyperclip.paste()

    if not get_login(mensagem1, "executado com sucesso"):
        return False

    send_key_press("losg\n")
    sleep(1)
    pyautogui.press('enter')
    for _ in range(9):
        send_key_press("\t")
    send_key_press("X\n")
    for _ in range(2):
        send_key_press("\t")
    send_key_press("X\n")
    return True


def set_user(user_target):
    send_key_press(user_target + "\n")
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')
    mensagem2 = pyperclip.paste()

    if get_login(mensagem2, "LIBERADO :"):
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
    return resultfinal


async def connect_to_websocket():
    secret_code = config("SECRETCODE")
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
    response_mail = new_military_registration_full('0556607')
    print("O resultado final é:")
    print(response_mail)
    # initialize_main()
