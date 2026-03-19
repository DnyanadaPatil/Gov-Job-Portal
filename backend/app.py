from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import datetime

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

users = {
    "admin@govtjobs.in": {"password": "secret123", "role": "admin", "name": "Admin User"},
    "rahul@example.com": {"password": "secret123", "role": "user", "name": "Rahul Sharma"}
}

jobs = [
    {"id": 1, "title": "Police Constable", "department": "Maharashtra Police", "location": "Mumbai", "salary": "25,000 - 35,000", "lastDate": "2026-04-30", "vacancies": 500, "qualification": "12th Pass"},
    {"id": 2, "title": "Junior Engineer", "department": "PWD Maharashtra", "location": "Pune", "salary": "35,000 - 50,000", "lastDate": "2026-05-15", "vacancies": 120, "qualification": "B.E. / Diploma"},
    {"id": 3, "title": "Clerk Grade II", "department": "Revenue Department", "location": "Nashik", "salary": "20,000 - 30,000", "lastDate": "2026-04-20", "vacancies": 300, "qualification": "Graduate"},
    {"id": 4, "title": "Forest Guard", "department": "Forest Department", "location": "Nagpur", "salary": "22,000 - 32,000", "lastDate": "2026-05-01", "vacancies": 200, "qualification": "12th Pass"}
]

applications = []

@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')
    if email in users and users[email]['password'] == password:
        user = users[email]
        return jsonify({"success": True, "token": "token-" + email, "user": {"email": email, "name": user['name'], "role": user['role']}})
    return jsonify({"success": False, "message": "Invalid email or password"}), 401

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    return jsonify({"success": True, "jobs": jobs})

@app.route('/api/apply', methods=['POST'])
def apply_job():
    data = request.get_json()
    applications.append({"id": len(applications)+1, "jobId": data.get('jobId'), "name": data.get('name'), "email": data.get('email'), "phone": data.get('phone')})
    return jsonify({"success": True, "message": "Application submitted!"})

@app.route('/api/applications', methods=['GET'])
def get_applications():
    return jsonify({"success": True, "applications": applications})

if __name__ == '__main__':
    print("Server running at http://localhost:3000")
    app.run(debug=True, port=3000, host='0.0.0.0')
