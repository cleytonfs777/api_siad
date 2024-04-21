import os
import smtplib
from email.message import EmailMessage
from decouple import config

def send_email(message_body, email_to):
    email = config("EMAILAPP")
    password = config("SENHAAPP")

    print(f"Email: {email}")
    print(f"Password: {password}")

    msg = EmailMessage()
    msg['Subject'] = 'Sua solicitação de Recuperação foi processada'
    msg['From'] = email
    msg['To'] = email_to
    msg.set_content(message_body)  # Use message_body aqui

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email, password)
            smtp.send_message(msg)
            return "Email enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar email: {e}"

if __name__ == '__main__':
    email_to = input('Digite seu email: ')
    message_body = input('Digite sua mensagem: ')
    send_email(message_body, email_to)
