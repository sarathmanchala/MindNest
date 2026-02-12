import datetime
from app.extensions import db
from datetime import datetime
from zoneinfo import ZoneInfo

def ist_now():
    return datetime.now(ZoneInfo("Asia/Kolkata"))


class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=True)
    mood_label = db.Column(db.String(100))
    ai_summary = db.Column(db.Text)
    advice = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=ist_now)
    mood_score = db.Column(db.Integer)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    user = db.relationship('User', back_populates="entries")

    def __repr__(self):
        return f'Entry {self.id} - {self.mood_label}'