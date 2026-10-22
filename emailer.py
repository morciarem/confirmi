import smtplib
import ssl
from email.message import EmailMessage
from config import email_settings



def send_email(to_email: str, verification_code: str):
    msg = EmailMessage()
    msg["From"] = email_settings.sender_email
    msg["To"] = to_email
    msg["Subject"] = email_settings.subject

    body = f"{email_settings.body}\n\n{verification_code}"
    msg.set_content(body)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            context=context,
            timeout=10,
        ) as server:
            server.login(
                email_settings.sender_email,
                email_settings.sender_password,
            )
            server.send_message(msg)

    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication failed: {e}", flush=True)

    except (TimeoutError, OSError) as e:
        print(f"Connection/network error: {e}", flush=True)

    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}", flush=True)

    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}", flush=True)
        raise
