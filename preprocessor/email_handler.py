# import smtplib
# from email.mime.text import MIMEText
# from config import SMTP_SERVER, SMTP_PORT, EMAIL_SENDER, EMAIL_PASSWORD, MAINTENANCE_EMAILS

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

#         print("Anomaly email sent successfully.")
#     except Exception as e:
#         print(f"Failed to send anomaly email: {str(e)}")

from mailersend import emails

# assigning NewEmail() without params defaults to MAILERSEND_API_KEY env var
mailer = emails.NewEmail(mailersend_api_key="mlsn.772a9a19a351368aa277f71ccf16457941e5120ce1b44b2fd6ff8ad15bd25032")

# def send_anomaly_email(subject, message):
#     """Send anomaly email notification."""
#     try:
#         # define an empty dict to populate with mail values
#         mail_body = {}

#         mail_from = {
#             "name": "Predictive-Ops",
#             "email": "MS_vtF2Dz@trial-3z0vkloymj1g7qrx.mlsender.net",
#         }

#         recipients = [
#             {
#                 "name": "Machine Engineer",
#                 "email": "gaerearge@yopmail.com",
#             }
#         ]

#         reply_to = [
#             {
#                 "name": "Predictive-Ops",
#                 "email": "MS_vtF2Dz@trial-3z0vkloymj1g7qrx.mlsender.net",
#             }
#         ]

#         mailer.set_mail_from(mail_from, mail_body)
#         mailer.set_mail_to(recipients, mail_body)
#         mailer.set_subject("Critical Alert: High Anomaly Count Detected", mail_body)
#         mailer.set_html_content(message, mail_body)
#         #mailer.set_plaintext_content("This is the text content", mail_body)
#         mailer.set_reply_to(reply_to, mail_body)

#         # using print() will also return status code and data
#         mailer.send(mail_body)

#         print("Anomaly email sent successfully.")
#     except Exception as e:
#         print(f"Failed to send anomaly email: {str(e)}")

def send_anomaly_email(subject, anomaly_summary, detailed_report):
    """Send a well-formatted anomaly email notification."""
    try:
        mail_body = {}

        mail_from = {"name": "Predictive-Ops", "email": "MS_vtF2Dz@trial-3z0vkloymj1g7qrx.mlsender.net"}
        recipients = [{"name": "Machine Engineer", "email": "gaerearge@yopmail.com"}]
        reply_to = [{"name": "Predictive-Ops", "email": "MS_vtF2Dz@trial-3z0vkloymj1g7qrx.mlsender.net"}]

        email_html = f"""
        <html>
        <body>
            <h2 style="color: red;">Critical Alert: High Anomaly Count Detected</h2>
            <p>The system has detected a high percentage of anomalies within the last 5 minutes.</p>

            <h3>Summary</h3>
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr>
                    <th>Sensor Type</th>
                    <th>Total Readings</th>
                    <th>Anomalies Detected</th>
                    <th>Percentage</th>
                </tr>
                {anomaly_summary}
            </table>

            <h3>Detailed Report</h3>
            <pre>{detailed_report}</pre>
        </body>
        </html>
        """

        mailer.set_mail_from(mail_from, mail_body)
        mailer.set_mail_to(recipients, mail_body)
        mailer.set_subject(subject, mail_body)
        mailer.set_html_content(email_html, mail_body)
        mailer.set_reply_to(reply_to, mail_body)

        mailer.send(mail_body)
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
