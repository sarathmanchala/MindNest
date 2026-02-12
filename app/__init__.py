from flask import Flask, render_template, url_for
from .config import Config
from .extensions import db, login_manager, migrate
from .journal import journal_bp
from .auth import auth_bp
import os
from .models import user, journal

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(journal_bp)
    app.register_blueprint(auth_bp)

    return app
