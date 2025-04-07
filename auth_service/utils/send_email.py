import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import HTTPException
import os

def send_email(recipient_email: str, code: int, email_type: str):
    # Настройка отправителя
    sender_email = os.getenv("EMAIL_USER")  # Используем переменную окружения для безопасности
    password = os.getenv("EMAIL_PASSWORD")

    # Настройка сообщения
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email

    if email_type == "confirmation":
        message["Subject"] = "Код подтверждения"
        body = f"Ваш код подтверждения: {code}"
    elif email_type == "password_reset":
        message["Subject"] = "Код для сброса пароля"
        body = f"Ваш код для сброса пароля: {code}"
    else:
        raise HTTPException(status_code=400, detail="Неверный тип email")

    message.attach(MIMEText(body, "plain"))

    try:
        # Подключение к SMTP серверу и отправка письма
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            text = message.as_string()
            server.sendmail(sender_email, recipient_email, text)
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при отправке email: {str(e)}")
