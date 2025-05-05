import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import aiosmtplib

load_dotenv(".env.local", override=True)

async def send_email(recipient_email: str, code: int, email_type: str):
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not sender_email or not password:
        print("❌ EMAIL_USER или EMAIL_PASSWORD не указаны")
        return

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email

    if email_type == "confirmation":
        message["Subject"] = "Код подтверждения"
        body = f"Ваш код подтверждения: {code}"
    elif email_type == "password_reset":
        message["Subject"] = "Сброс пароля для вашего аккаунта"
        body = (
            f"Вы запросили сброс пароля.\n"
            f"Введите следующий код для подтверждения:\n\n"
            f"{code}\n\n"
            f"Если вы не запрашивали сброс — просто проигнорируйте это письмо."
        )

    else:
        print("❌ Неизвестный тип email:", email_type)
        return

    message.attach(MIMEText(body, "plain"))

    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_server,
            port=smtp_port,
            username=sender_email,
            password=password,
            start_tls=True,
        )
        print(f"✅ Email отправлен на {recipient_email}")
    except aiosmtplib.SMTPAuthenticationError:
        print("❌ Ошибка авторизации. Проверь EMAIL_USER и EMAIL_PASSWORD.")
    except Exception as e:
        print(f"❌ Ошибка при отправке email: {e}")
