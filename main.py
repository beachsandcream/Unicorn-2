from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app and SQLAlchemy for database interactions
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///unicorn_resumes.db')  # Use Heroku's DATABASE_URL or local SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Resume model for the database
class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.Text, nullable=True)  # Parsed skills stored as a comma-separated string
    certifications = db.Column(db.Text, nullable=True)  # Certifications stored as a comma-separated string
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    resume_file_path = db.Column(db.String(200), nullable=False)  # Path to the uploaded resume

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "skills": self.skills.split(",") if self.skills else [],
            "certifications": self.certifications.split(",") if self.certifications else [],
            "upload_date": self.upload_date.isoformat(),
            "resume_file_path": self.resume_file_path
        }

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

# Endpoint to upload resumes
@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    name = request.form.get('name')
    email = request.form.get('email')
    file = request.files['resume']

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    # Ensure directory exists
    os.makedirs('resumes', exist_ok=True)
    file_path = f"resumes/{file.filename}"
    file.save(file_path)

    new_resume = Resume(
        name=name,
        email=email,
        resume_file_path=file_path
    )
    db.session.add(new_resume)
    db.session.commit()

    return jsonify({"message": "Resume uploaded successfully", "resume": new_resume.to_dict()}), 201

# Endpoint to retrieve all resumes
@app.route('/resumes', methods=['GET'])
def get_resumes():
    resumes = Resume.query.all()
    return jsonify({"resumes": [resume.to_dict() for resume in resumes]}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))