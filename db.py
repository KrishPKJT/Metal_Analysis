import os

class Config:
    # You can use environment variables for security or just hardcode your settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/wistron')
    SQLALCHEMY_TRACK_MODIFICATIONS = False