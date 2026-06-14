from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from app.core.config import settings


def send_reset_email(to_email: str, password: str, user_name: str = "", is_temp_password: bool = True):

    subject = "🔐 Your New Password"

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:Arial;background:#f5f5f5;padding:20px;">
        <div style="max-width:500px;margin:auto;background:white;padding:20px;border-radius:10px;">
            
            <h2>Hello {user_name or "User"} 👋</h2>

            <p>Your new password is:</p>

            <h1 style="color:#2563eb;letter-spacing:2px;">
                {password}
            </h1>

            <p>Please login and change it immediately.</p>

            <hr>

            <p style="font-size:12px;color:red;">
                ⚠️ Do not share this password with anyone.
            </p>

        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = to_email

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        print("✅ Email sent successfully")
        return True

    except Exception as e:
        print("❌ Email error:", e)
        return False