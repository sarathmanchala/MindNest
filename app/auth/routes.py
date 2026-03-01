from flask import Blueprint, redirect, render_template, session, url_for, request, current_app
from flask_login import login_user, logout_user
import requests
from app.extensions import db
from app.models import User, user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login")
def login():
    return render_template("auth/login.html")

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

@auth_bp.route("/login/google")
def google_login():
    cfg = current_app.config

    google_auth_url = (
        f"{cfg['GOOGLE_AUTHORIZE_URL']}?"
        f"client_id={cfg['GOOGLE_CLIENT_ID']}&"
        f"redirect_uri={cfg['GOOGLE_REDIRECT_URI']}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline&"
        f"prompt=consent"
    )

    return redirect(google_auth_url)

@auth_bp.route("/callback/google")
def google_callback():
    code = request.args.get("code")
    if not code:
        return "Missing code from Google", 400

    cfg = current_app.config

    # Exchange code → token
    token_resp = requests.post(
        cfg["GOOGLE_TOKEN_URL"],
        data={
            "client_id": cfg["GOOGLE_CLIENT_ID"],
            "client_secret": cfg["GOOGLE_CLIENT_SECRET"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": cfg["GOOGLE_REDIRECT_URI"],
        },
    ).json()

    access_token = token_resp.get("access_token")
    if not access_token:
        return f"Token error: {token_resp}", 400

    # Fetch Google user info
    user_data = requests.get(
        cfg["GOOGLE_USERINFO_URL"],
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    if "sub" not in user_data:
        return f"Google user error: {user_data}", 400

    google_id = user_data["sub"]
    email = user_data.get("email")
    username = user_data.get("name")

    # First check by google_id
    user = User.query.filter_by(google_id=google_id).first()

    if not user:
        # Check if email already exists
        user = User.query.filter_by(email=email).first()

        if user:
            # Link Google account to existing user
            user.google_id = google_id
            db.session.commit()
        else:
            # Create completely new user
            user = User(
                google_id=google_id,
                username=username,
                email=email,
            )
            user.set_password(username)
            db.session.add(user)
            db.session.commit()
    session["access_token"] = access_token
    if user:
        user = User.query.filter_by(email=email).first()
        login_user(user)
    return redirect(url_for("journal.index"))

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
    print("Github username is", username)
    if not user:
        user = User(
            github_id=github_id,
            username=username,
            email=email,
        )
        print("Github username is", username)
        user.set_password(username)
        db.session.add(user)
        db.session.commit()
    session["access_token"] = access_token
    login_user(user)
    return redirect(url_for("journal.index"))


@auth_bp.route("/login-user", methods=["POST"])
def login_username():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    print("Email:", email)
    if not email or not password:
        return {"error": "Email and password required"}, 400
    user = User.query.filter_by(email=email).first()
    if not user:
        return {"error": "Invalid email"}, 401
    if not user.check_password(password):
        return {"error": "Invalid password"}, 401
    login_user(user, remember=True)
    return {"message": "Login successful", "redirect": url_for("journal.index")}, 200