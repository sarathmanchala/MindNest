from flask import Blueprint, redirect, render_template, session, url_for, request, current_app
from flask_login import login_user, logout_user
import requests
from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login")
def login():
    return render_template("journal/login.html")

@auth_bp.route("/login/github")
def github_login():
    cfg = current_app.config
    github_auth_url = (
        f"{cfg['AUTHORIZE_URL']}?"
        f"client_id={cfg['CLIENT_ID']}&"
        f"scope=user:email&"
        f"prompt=consent"
    )
    return redirect(github_auth_url)

@auth_bp.route("/logout")
def logout():
    token = session.get("access_token")
    cfg = current_app.config
    if token:
        requests.delete(
            f"https://api.github.com/applications/{cfg['CLIENT_ID']}/token",
            auth=(cfg['CLIENT_ID'], cfg['CLIENT_SECRET']),
            json={"access_token": token}
        )
    logout_user()
    session.clear()
    return redirect(url_for("auth.login"))

@auth_bp.route("/callback/github")
def github_callback():
    code = request.args.get("code")
    if not code:
        return "Missing code from GitHub", 400

    cfg = current_app.config

    # Exchange code → token
    token_resp = requests.post(
        cfg["TOKEN_URL"],
        headers={"Accept": "application/json"},
        data={
            "client_id": cfg["CLIENT_ID"],
            "client_secret": cfg["CLIENT_SECRET"],
            "code": code,
        }
    ).json()

    access_token = token_resp.get("access_token")
    if not access_token:
        return f"Token error: {token_resp}", 400

    # Fetch GitHub user
    user_data = requests.get(
        cfg["USER_API"],
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    if "id" not in user_data:
        return f"GitHub user error: {user_data}", 400

    # Fetch email
    email_resp = requests.get(
        cfg["EMAIL_API"],
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json"
        }
    )
    email_data = email_resp.json()
    email = None
    if isinstance(email_data, list):
        for e in email_data:
            if e.get("primary") and e.get("verified"):
                email = e["email"]
                break
    else:
        current_app.logger.error(f"Github email error: {email_data}")
    if not email:
        email = user_data.get("email")
    github_id = str(user_data["id"])
    username = user_data["login"]
    user = User.query.filter_by(github_id=github_id).first()
    if not user:
        user = User(
            github_id=github_id,
            username=username,
            email=email
        )
        db.session.add(user)
        db.session.commit()
    session["access_token"] = access_token
    login_user(user)
    return redirect(url_for("journal.index"))
