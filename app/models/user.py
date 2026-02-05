from flask_login import UserMixin
from ..extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
