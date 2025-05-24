import os
from dotenv import load_dotenv

load_dotenv()

EVENT_HUB_CONNECTION_STRING = os.getenv("EVENT_HUB_CONNECTION_STRING")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")

CONSUMER_GROUP = os.getenv("CONSUMER_GROUP")
ROLLING_WINDOW_SIZE = os.getenv("ROLLING_WINDOW_SIZE")  # Number of samples in the rolling window

# Email Config
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD =  os.getenv("EMAIL_PASSWORD")
MAINTENANCE_EMAILS = os.getenv("MAINTENANCE_EMAILS", "").split(",")