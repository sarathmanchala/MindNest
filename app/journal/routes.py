from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Blueprint, render_template,jsonify, request
from flask_login import current_user, login_required
import os
import json
from google import genai
from google.genai import types
from app.models import JournalEntry, User
from app.extensions import db
from groq import Groq

groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

journal_bp = Blueprint("journal", __name__, url_prefix="/")


def ist_now():
    return datetime.now(ZoneInfo("Asia/Kolkata"))

def get_mood_class(score):
    if score >= 8:
        return "bg-success"
    elif score >= 5:
        return "bg-warning text-dark"
    else:
        return "bg-danger"


@journal_bp.route("/")
@login_required
def index():
    return render_template("journal/index.html")

@journal_bp.route("/contact")
@login_required
def contact():
    return render_template("journal/contact.html")

@journal_bp.route("/entry")
@login_required
def entry():
    return render_template("journal/entry.html")

@journal_bp.route("/analyze", methods=["POST"])
@login_required
def analyze():
    data = request.get_json()
    user_feelings = data.get('text')

    system_prompt = """You are an empathetic wellness assistant trained in emotional intelligence and supportive communication. Analyze the user’s journal entry to identify emotions, stressors, thought patterns, and unspoken concerns. Respond in a warm, non-judgmental tone that validates the user’s feelings. Provide gentle insights, emotional reflections, and optional coping or self-care suggestions. Do not diagnose or give medical advice. 

Return ONLY a valid JSON object with:
{
  "summary": "2-sentence empathetic reflection",
  "mood_label": "one word mood",
  "advice": "one actionable advice",
  "score": number between 1 and 10
}
"""

    try:
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",  # Very good model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_feelings}
            ],
            temperature=0.7
        )

        ai_text = completion.choices[0].message.content

        # Sometimes models add extra text → extract JSON safely
        import re
        json_match = re.search(r"\{.*\}", ai_text, re.DOTALL)
        if not json_match:
            return jsonify({"error": "Invalid AI response"}), 500

        ai_response = json.loads(json_match.group())

        entry = JournalEntry(
            content=user_feelings,
            mood_label=ai_response.get("mood_label"),
            advice=ai_response.get("advice"),
            mood_score=ai_response.get("score"),
            timestamp=ist_now(),
            user_id=current_user.id,
            ai_summary=ai_response.get("summary")
        )

        db.session.add(entry)
        db.session.commit()

        score = ai_response.get("score")
        ai_response["mood_class"] = get_mood_class(score)

        return jsonify(ai_response)

    except Exception as e:
        print(f"Error during AI generation: {e}")
        return jsonify({"error": "Failed to generate response"}), 500
    

@journal_bp.route("/history")
@login_required
def history():
    ist = ZoneInfo("Asia/Kolkata")
    seven_days_ago = datetime.now(ist) - timedelta(days=7)
    entries = JournalEntry.query.filter(JournalEntry.user_id == current_user.id, JournalEntry.timestamp >= seven_days_ago).order_by(JournalEntry.timestamp.desc()).all()
    for entry in entries:
        entry.mood_class = get_mood_class(entry.mood_score)
    return render_template("journal/history.html", entries=entries)

@journal_bp.route("/entry/<string:query>", methods=["GET"])
@login_required
def search_entry(query):
    entries = JournalEntry.query.filter(JournalEntry.user_id == current_user.id, JournalEntry.content.ilike(f"%{query}%")).order_by(JournalEntry.timestamp.desc()).all()
    results = []
    for entry in entries:
        results.append({
            "id": entry.id,
            "content": entry.content,
            "mood_score": entry.mood_score,
            "mood_label": entry.mood_label,
            "advice": entry.advice,
            "timestamp": entry.timestamp.strftime("%B %d, %Y")
        })
    print(f"Search results for '{query}': {results}")
    return jsonify(results)

@journal_bp.route("/delete/<int:entry_id>", methods=["DELETE"])
@login_required
def delete_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"success": True})

