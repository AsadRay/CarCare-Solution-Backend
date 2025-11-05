import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS Configuration
    CORS_HEADERS = 'Content-Type'
    
    # SocketIO Configuration
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    
    # Notification APIs
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

    
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = bool(int(os.getenv("MAIL_USE_TLS", 1)))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL')
    
    # Business Logic
    BOOKING_BUFFER_MINUTES = 15  # Buffer between appointments
    CANCELLATION_WINDOW_HOURS = 24  # Hours before appointment to allow cancellation
    BUSINESS_HOURS_START = 8  # 8 AM
    BUSINESS_HOURS_END = 18  # 6 PM

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
