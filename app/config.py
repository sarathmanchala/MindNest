import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", 'postgresql://postgres:Teja%402003@localhost:5432/mindnest')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLIENT_ID = os.getenv("CLIENT_ID", "Ov23lifXArPGz7aE0VL8")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", "29cf62d54599c77180909688251f997ececd5f29")
    AUTHORIZE_URL = os.getenv("AUTHORIZE_URL", "https://github.com/login/oauth/authorize")
    TOKEN_URL = os.getenv("TOKEN_URL", "https://github.com/login/oauth/access_token")
    USER_API = os.getenv("USER_API", "https://api.github.com/user")
    EMAIL_API = os.getenv("EMAIL_API", "https://api.github.com/user/emails")
    SCOPES = ['useremail']
    SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    }
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    GOOGLE_AUTHORIZE_URL = os.getenv("GOOGLE_AUTHORIZE_URL")
    GOOGLE_TOKEN_URL = os.getenv("GOOGLE_TOKEN_URL")
    GOOGLE_USERINFO_URL = os.getenv("GOOGLE_USERINFO_URL")

    