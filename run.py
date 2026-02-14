from dotenv import load_dotenv
load_dotenv()
from app import create_app
from flask_migrate import upgrade
app = create_app()
from app import db 

if __name__ == '__main__':
    app.run(debug=True)