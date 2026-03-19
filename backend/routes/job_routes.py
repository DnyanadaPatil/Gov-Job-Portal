# ================================================================
# 📄 FILE: job_routes.py
# 📂 FOLDER: backend/routes/
# 🎯 YEH KYA KARTA HAI?
#    Jobs se related sab kuch:
#    - Sab jobs dikhana (GET /api/jobs)
#    - Ek job ke details (GET /api/jobs/<id>)
#    - Naya job add karna — admin (POST /api/jobs)
#    - Job edit karna — admin (PUT /api/jobs/<id>)
#    - Job delete karna — admin (DELETE /api/jobs/<id>)
#
# 🔤 HTTP METHODS yaad rakho:
#    GET    = sirf data maango (kuch badlo nahi)
#    POST   = naya data bhejo (create karo)
#    PUT    = purana data update karo
#    DELETE = data hatao
# ================================================================

from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime, timezone
from data.db import read_db, write_db
from middleware.auth import token_required, admin_required

# Blueprint for jobs routes
job_bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')


# ================================================================
# ROUTE 1: Sab jobs lo (with search/filter)
# URL: GET /api/jobs
# URL: GET /api/jobs?search=engineer
# URL: GET /api/jobs?department=Health
#
# Public route — koi bhi dekh sakta hai, login zaroori nahi
# ================================================================
@job_bp.route('/', methods=['GET'])
def get_all_jobs():
    db = read_db()
    jobs = db['jobs']   # Sirf jobs list lo

    # --------------------------------------------------------
    # SEARCH FEATURE
    # 🔤 request.args.get() = URL ke ?search=... wala part padho
    #    Example: /api/jobs?search=engineer
    #    request.args.get('search') = 'engineer'
    # --------------------------------------------------------
    search = request.args.get('search', '').lower()
    department = request.args.get('department', '')

    # Agar search text hai toh filter karo
    if search:
        # List comprehension = ek line mein filtering
        # [j for j in jobs if condition] = woh jobs rakho jahan condition sahi ho
        # JavaScript mein .filter() tha — Python mein yeh cleaner hai!
        jobs = [j for j in jobs if
                search in j['title'].lower() or
                search in j['department'].lower() or
                search in j['description'].lower()]

    # Department filter
    if department and department != 'all':
        jobs = [j for j in jobs if j['department'] == department]

    # Newest jobs pehle (date ke hisaab se sort)
    # key=lambda j: j['createdAt'] = sort karne ke liye kaunsa field use karo
    # reverse=True = bada pehle (newest pehle)
    jobs = sorted(jobs, key=lambda j: j['createdAt'], reverse=True)

    return jsonify(jobs)


# ================================================================
# ROUTE 2: Ek specific job lo
# URL: GET /api/jobs/job-001
#
# 🔤 <job_id> = URL parameter
#    Flask mein yeh aise likhte hain: '/api/jobs/<job_id>'
#    JavaScript/Express mein tha: '/api/jobs/:id'
#    Jab user /api/jobs/job-001 pe jaata hai,
#    Flask automatically job_id = 'job-001' set kar deta hai
# ================================================================
@job_bp.route('/<job_id>', methods=['GET'])
def get_job(job_id):
    db = read_db()

    # job_id se job dhundho
    job = next((j for j in db['jobs'] if j['id'] == job_id), None)

    # Agar nahi mila
    if not job:
        return jsonify({'message': 'Job nahi mili.'}), 404  # 404 = Not Found

    return jsonify(job)


# ================================================================
# ROUTE 3: Naya job add karo (ADMIN ONLY)
# URL: POST /api/jobs
#
# 🔤 DON'T DECORATORS KA KAAM:
#    @token_required  = pehle check: logged in hai?
#    @admin_required  = phir check: admin hai?
#    def create_job() = phir yeh chala
#
#    Order important hai! Hamesha token_required pehle
# ================================================================
@job_bp.route('/', methods=['POST'])
@token_required
@admin_required
def create_job():
    data = request.get_json()

    # Sab required fields nikalo
    title = data.get('title', '').strip()
    department = data.get('department', '').strip()
    qualification = data.get('qualification', '').strip()
    salary = data.get('salary', '').strip()
    last_date = data.get('lastDate', '')
    description = data.get('description', '').strip()
    vacancies = data.get('vacancies', 1)
    location = data.get('location', 'Maharashtra').strip()

    # Validation
    if not all([title, department, qualification, salary, last_date, description]):
        # all([...]) = check karo sab values truthy hain
        return jsonify({'message': 'Sab required fields bharo.'}), 400

    db = read_db()

    # Naya job object
    new_job = {
        'id': str(uuid.uuid4()),
        'title': title,
        'department': department,
        'qualification': qualification,
        'salary': salary,
        'lastDate': last_date,
        'description': description,
        'vacancies': int(vacancies),     # int() = string ko number mein badlo
        'location': location,
        'createdAt': datetime.now(timezone.utc).isoformat()
    }

    db['jobs'].append(new_job)
    write_db(db)

    return jsonify({'message': 'Job post ho gayi!', 'job': new_job}), 201


# ================================================================
# ROUTE 4: Job update karo (ADMIN ONLY)
# URL: PUT /api/jobs/<job_id>
# ================================================================
@job_bp.route('/<job_id>', methods=['PUT'])
@token_required
@admin_required
def update_job(job_id):
    db = read_db()

    # Job ki position dhundho list mein
    # enumerate() = list ke saath index bhi do
    # ((i, j) for i, j in enumerate(db['jobs']) if j['id'] == job_id)
    job_index = next((i for i, j in enumerate(db['jobs']) if j['id'] == job_id), None)

    if job_index is None:
        return jsonify({'message': 'Job nahi mili.'}), 404

    data = request.get_json()

    # Existing job mein naye fields merge karo
    # .update() = dictionary mein nayi values add/overwrite karo
    # JavaScript mein {...existing, ...newData} tha
    db['jobs'][job_index].update({
        'title': data.get('title', db['jobs'][job_index]['title']),
        'department': data.get('department', db['jobs'][job_index]['department']),
        'qualification': data.get('qualification', db['jobs'][job_index]['qualification']),
        'salary': data.get('salary', db['jobs'][job_index]['salary']),
        'lastDate': data.get('lastDate', db['jobs'][job_index]['lastDate']),
        'description': data.get('description', db['jobs'][job_index]['description']),
        'vacancies': data.get('vacancies', db['jobs'][job_index]['vacancies']),
        'location': data.get('location', db['jobs'][job_index]['location']),
    })

    write_db(db)

    return jsonify({'message': 'Job update ho gayi!', 'job': db['jobs'][job_index]})


# ================================================================
# ROUTE 5: Job delete karo (ADMIN ONLY)
# URL: DELETE /api/jobs/<job_id>
# ================================================================
@job_bp.route('/<job_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_job(job_id):
    db = read_db()

    # Job dhundho
    job = next((j for j in db['jobs'] if j['id'] == job_id), None)
    if not job:
        return jsonify({'message': 'Job nahi mili.'}), 404

    # List se remove karo
    # list comprehension se naya list banao BINA is job ke
    # JavaScript mein .filter() tha same kaam ke liye
    db['jobs'] = [j for j in db['jobs'] if j['id'] != job_id]

    write_db(db)

    return jsonify({'message': 'Job delete ho gayi.'})
