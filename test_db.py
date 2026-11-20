from flask import Flask
from sqlalchemy import text
from extensions import db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():

    try:
        result = db.session.execute(
            text("SELECT DATABASE()")
        )

        database_name = result.scalar()

        print("\n SUCCESS! MySQL connected.")
        print("Connected database:", database_name)

    except Exception as e:
        print("\n Database connection failed.")
        print("Error:", e)

    finally:
        db.session.remove()