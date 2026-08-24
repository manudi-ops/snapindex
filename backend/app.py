from flask import Flask
from flask_cors import CORS
from db.models import db, Category
from auth.routes import auth_bp, bcrypt
from ingestion.routes import ingestion_bp
from search.routes import search_bp
from classification.routes import classification_bp
from neglect.routes import neglect_bp

app = Flask(__name__) 
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///snapindex.db"
db.init_app(app)
bcrypt.init_app(app)
app.register_blueprint(auth_bp)
app.register_blueprint(ingestion_bp)
app.register_blueprint(search_bp)
app.register_blueprint(classification_bp)
app.register_blueprint(neglect_bp)

DEFAULT_CATEGORIES = [
    ("Programming & Software Development", "Programming and software development: code, algorithms, functions, debugging, software design, programming languages, source code examples"),
    ("Databases", "Databases: SQL, relational database design, normalization, ER diagrams, queries, database management systems"),
    ("Networks & Systems", "Computer networks and systems: TCP/IP, network protocols, servers, operating systems, system administration, infrastructure"),
    ("Web & Mobile Development", "Web and mobile application development: HTML, CSS, JavaScript, frontend, backend, APIs, mobile apps, user interfaces"),
    ("Artificial Intelligence & Data Science", "Artificial intelligence, machine learning and data science: models, datasets, algorithms, data analysis, neural networks, statistics"),
    ("Business & Requirements Analysis", "Business analysis and requirements gathering: stakeholder interviews, business processes, requirements specification, project scope, feasibility"),
    ("Research Methods & Documentation", "Academic research methods and documentation: literature review, methodology, questionnaires, reports, citations, dissertation writing"),
    ("Mathematics & Statistics", "Mathematics and statistics: equations, formulas, calculations, statistical analysis, probability"),
    ("General / Uncategorized", "General or uncategorized academic material that does not clearly fit another category"),
]

with app.app_context():
    db.create_all()
    if Category.query.count() == 0:
        for name, desc in DEFAULT_CATEGORIES:
            db.session.add(Category(categoryName=name, description=desc))
        db.session.commit()
        print(f"Seeded {len(DEFAULT_CATEGORIES)} default categories.")

@app.route("/")
def health_check():
    return {"status": "SnapIndex backend is running"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)