from flask import Flask
from flask_cors import CORS
from db.models import db
from auth.routes import auth_bp, bcrypt

app = Flask(__name__) 
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///snapindex.db"
db.init_app(app)
bcrypt.init_app(app)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

@app.route("/")
def health_check():
    return {"status": "SnapIndex backend is running"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)