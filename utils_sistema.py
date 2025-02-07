import os
from time import sleep
import random
from pyautogui import write, hotkey, press
import pyperclip
import subprocess
from dotenv import load_dotenv
import requests
import json
import psutil

load_dotenv()  # take environment variables from .env.


def inicia_sistema():

    # Carrega variaveis do sistema
    alvo = os.getenv('SYSTEM')
    usuario =  os.getenv('MYNUMBER')
    senha = os.getenv('MYPASS')
    caminho_pw3270 = os.getenv('CAMINHO_ARQ')
    intervalo_teclas = os.getenv('ITV_TECLAS')
    intervalo_teclas = int(intervalo_teclas)
    sistema = os.getenv('SYSTEM')
    secret_code = os.getenv('SECRETCODE')
    url_email = os.getenv('URL_EMAIL')
    email_admin = os.getenv('EMAIL_USER_ADMIN')


    def update_env_variable(key, value, env_file=".env"):
        """Atualiza ou adiciona uma variável no arquivo .env"""
        lines = []
        key_found = False

        # Ler o arquivo .env e modificar a linha correspondente
        if os.path.exists(env_file):
            with open(env_file, "r") as file:
                for line in file:
                    if line.startswith(f"{key}="):  # Se a variável já existe, modifica ela
                        lines.append(f"{key}={value}\n")
                        key_found = True
                    else:
                        lines.append(line)

        # Se a variável não for encontrada, adiciona ao final do arquivo
        if not key_found:
            lines.append(f"{key}={value}\n")

        # Escreve as alterações de volta no .env
        with open(env_file, "w") as file:
            file.writelines(lines)

        # Recarrega as variáveis do .env
        load_dotenv(override=True)


    def enviar_email(mensagem, email):
            
        try:

            headers = {'Content-Type': 'application/json'}

            response_body = {
            "token": secret_code,
            "email": email,
            "message":mensagem
            }

            requests.post(url_email, headers=headers,
                        data=json.dumps(response_body))
            return "Email enviado com sucesso para {}"
        except Exception as e:
            return f"Erro: {e}"
        


    def abrir_arquivo(caminho_arquivo):
        if os.path.exists(caminho_arquivo):
            subprocess.Popen(caminho_arquivo, shell=True)
            print(f"Arquivo aberto com sucesso: {caminho_arquivo}")
        else:
            print("Erro: O arquivo especificado não foi encontrado.")

    def gerar_nova_senha():
        consoantes = list("bcdfghjklmnpqrstvwxyz")
        numeros = list("123456789")
        password = "".join(random.choices(consoantes, k=4)) + "".join(random.choices(numeros, k=4))
        return password

    def digitar_dados(senha):

        sleep(1)  # Garantir que o foco esteja na aplicação correta
        # Sistema a ser acessado
        write("CBMMG")
        sleep(intervalo_teclas / 1000)
        press("tab")
        sleep(intervalo_teclas / 1000)
        # Insere o usuario
        write(usuario)
        sleep(intervalo_teclas / 1000)
        press("tab")
        sleep(intervalo_teclas / 1000)
        # Insere a senha
        write(senha)
        sleep(intervalo_teclas / 1000)
        press("enter")
        sleep(2)
        
        # Verificar através de copiar e colar para a saida se foi sucesso
        while True:
            hotkey("ctrl", "a")
            sleep(0.5)
            hotkey("ctrl", "c")
            sleep(0.5)
            press("esc")
            mensagem1 = pyperclip.paste()
            
            if "Senha expirada" in mensagem1:
                print(f"A senha atual é: {senha}")
                
                write(senha)

                sleep(intervalo_teclas / 1000)
                nova_senha = gerar_nova_senha()

                # Gerada nova senha deve salvar nas variaveis de ambiente, recarrega-las e enviar email ao user admin
                senha = nova_senha
                # Enviando email
                msg = f"Sua senha de admin foi refefinida para {senha}"
                enviar_email(msg, email_admin)
                # Atualiza variáveis de ambiente
                update_env_variable("MYPASS", senha)


                write(senha)
                sleep(intervalo_teclas / 1000)
                press("enter")
                sleep(intervalo_teclas / 1000)
                
                write(senha)
                sleep(intervalo_teclas / 1000)
                press("enter")
                sleep(intervalo_teclas / 1000)
                
                print(f"A nova senha é: {senha}")
            
            elif "Logon executado com sucesso" in mensagem1:
                write(sistema)
                sleep(intervalo_teclas / 1000)
                press("enter")
                break
            else:
                press("enter")
                sleep(intervalo_teclas / 1000)

    abrir_arquivo(caminho_pw3270)
    sleep(3)  # Aguardar para garantir que o programa esteja aberto
    digitar_dados(senha)

def kill_processes_by_name(keyword):
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            process_name = process.info['name']
            process_pid = process.info['pid']
            if keyword.lower() in process_name.lower():
                print(f"Encerrando processo: {process_name} (PID: {process_pid})")
                psutil.Process(process_pid).terminate()  # Encerra o processo
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass




if __name__ == "__main__":
    # Inicia o Sistema
    # inicia_sistema()

    # Chamando a função para encerrar processos com "w3270" no nome
    kill_processes_by_name("w3270")
    
