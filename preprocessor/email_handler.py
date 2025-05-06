import smtplib
from email.mime.text import MIMEText
from config import SMTP_SERVER, SMTP_PORT, EMAIL_SENDER, EMAIL_PASSWORD, MAINTENANCE_EMAILS

def send_anomaly_email(subject, message):
    """Send anomaly email notification."""
    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = ", ".join(MAINTENANCE_EMAILS)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, MAINTENANCE_EMAILS, msg.as_string())

        print("Anomaly email sent successfully.")
    except Exception as e:
        print(f"Failed to send anomaly email: {str(e)}")


# import smtplib
# from email.mime.text import MIMEText
# from app.config import SMTP_SERVER, SMTP_PORT, EMAIL_SENDER, EMAIL_PASSWORD, MAINTENANCE_EMAILS

# def send_anomaly_email(subject, message):
#     """Send anomaly email notification."""
#     try:
#         msg = MIMEText(message)
#         msg["Subject"] = subject
#         msg["From"] = EMAIL_SENDER
#         msg["To"] = ", ".join(MAINTENANCE_EMAILS)

#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(EMAIL_SENDER, EMAIL_PASSWORD)
#             server.sendmail(EMAIL_SENDER, MAINTENANCE_EMAILS, msg.as_string())
#     except Exception as e:
#         print(f"Failed to send email: {e}")


# def send_detailed_anomaly_email(subject, content):
#     try:
#         msg = MIMEText(content)
#         msg['Subject'] = subject
#         msg['From'] = EMAIL_SENDER
#         msg['To'] = MAINTENANCE_EMAILS[0]

#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(EMAIL_SENDER, EMAIL_PASSWORD)
#             server.send_message(msg)
#         print("Detailed anomaly email sent.")
#     except Exception as e:
#         print(f"Error sending email: {str(e)}")
