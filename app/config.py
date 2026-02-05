import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", 'postgresql://postgres:Teja%402003@localhost:5432/trivia_quiz')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLIENT_ID = "Ov23lifXArPGz7aE0VL8"
    CLIENT_SECRET = "29cf62d54599c77180909688251f997ececd5f29"
    AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    USER_API = "https://api.github.com/user"
    EMAIL_API = "https://api.github.com/user/emails"
    SCOPES = ['useremail']
    