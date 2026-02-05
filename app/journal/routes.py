from flask import Blueprint, render_template
from flask_login import login_required
from dotenv import load_dotenv
import os
import google.generativeai as genai



load_dotenv()
journal_bp = Blueprint("journal", __name__, url_prefix="/")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
print("API key loaded:", os.getenv("GEMINI_API_KEY") is not None)

@journal_bp.route("/")
@login_required
def index():
    return render_template("journal/index.html")




@journal_bp.route("/contact")
@login_required
def contact():
    return render_template("journal/contact.html")