from dotenv import load_dotenv
load_dotenv()
from app import create_app
from flask_migrate import upgrade
app = create_app()
from app import db 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)