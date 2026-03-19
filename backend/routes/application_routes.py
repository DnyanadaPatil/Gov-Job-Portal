# ================================================================
# 📄 FILE: application_routes.py
# 📂 FOLDER: backend/routes/
# 🎯 YEH KYA KARTA HAI?
#    Job applications se related sab routes:
#    - Apply karna (user)
#    - Apni applications dekhna (user)
#    - Sab applications dekhna (admin)
#    - Application status update karna (admin)
#    - Dashboard ke stats (admin)
# ================================================================

from flask import Blueprint, request, jsonify, g
import uuid
from datetime import datetime, timezone
from data.db import read_db, write_db
from middleware.auth import token_required, admin_required

app_bp = Blueprint('applications', __name__, url_prefix='/api/applications')


# ================================================================
# ROUTE 1: Job ke liye apply karo
# URL: POST /api/applications/apply
# Sirf logged-in users apply kar sakte hain
# ================================================================
@app_bp.route('/apply', methods=['POST'])
@token_required
def apply_for_job():
    data = request.get_json()

    job_id = data.get('jobId', '')
    phone = data.get('phone', '').strip()
    dob = data.get('dob', '')
    qualification = data.get('qualification', '').strip()
    experience = data.get('experience', 'Fresher').strip()
    address = data.get('address', '').strip()

    # Sab fields check karo
    if not all([job_id, phone, dob, qualification, address]):
        return jsonify({'message': 'Sab required fields bharo.'}), 400

    db = read_db()

    # CHECK 1: Kya yeh job exist karti hai?
    job = next((j for j in db['jobs'] if j['id'] == job_id), None)
    if not job:
        return jsonify({'message': 'Yeh job nahi mili.'}), 404

    # CHECK 2: Kya user pehle se apply kar chuka hai is job ke liye?
    # g.current_user = woh user jo logged in hai (token se mila)
    already_applied = next(
        (a for a in db['applications']
         if a['jobId'] == job_id and a['userId'] == g.current_user['id']),
        None
    )
    if already_applied:
        return jsonify({'message': 'Aap pehle se is job ke liye apply kar chuke hain.'}), 400

    # CHECK 3: Kya last date nikal gayi?
    # datetime.strptime() = string ko date object mein badlo
    # '%Y-%m-%d' = date format (2025-12-31)
    last_date = datetime.strptime(job['lastDate'], '%Y-%m-%d')
    if last_date < datetime.now():
        return jsonify({'message': 'Is job ki last date nikal gayi hai.'}), 400

    # Naya application banao
    new_app = {
        'id': str(uuid.uuid4()),
        'jobId': job_id,
        'userId': g.current_user['id'],         # Token se mila
        'applicantName': g.current_user['name'], # Token se mila (tamper-proof)
        'applicantEmail': g.current_user['email'],
        'phone': phone,
        'dob': dob,
        'qualification': qualification,
        'experience': experience,
        'address': address,
        'status': 'Pending',                    # Hamesha Pending se shuru
        'appliedAt': datetime.now(timezone.utc).isoformat()
    }

    db['applications'].append(new_app)
    write_db(db)

    return jsonify({'message': 'Application submit ho gayi!', 'application': new_app}), 201


# ================================================================
# ROUTE 2: Meri apni applications (user)
# URL: GET /api/applications/my
# ================================================================
@app_bp.route('/my', methods=['GET'])
@token_required
def get_my_applications():
    db = read_db()

    # Sirf is user ki applications
    my_apps = [a for a in db['applications'] if a['userId'] == g.current_user['id']]

    # Har application mein job ka title bhi add karo
    # (application mein sirf jobId hai, title nahi)
    result = []
    for app in my_apps:
        job = next((j for j in db['jobs'] if j['id'] == app['jobId']), None)
        # dict ki copy banao (original mat badlo)
        app_with_job = dict(app)
        app_with_job['jobTitle'] = job['title'] if job else 'Job Hata Di Gayi'
        app_with_job['department'] = job['department'] if job else '-'
        result.append(app_with_job)

    # Newest pehle
    result.sort(key=lambda a: a['appliedAt'], reverse=True)

    return jsonify(result)


# ================================================================
# ROUTE 3: Sab applications (ADMIN ONLY)
# URL: GET /api/applications/all
# ================================================================
@app_bp.route('/all', methods=['GET'])
@token_required
@admin_required
def get_all_applications():
    db = read_db()

    result = []
    for app in db['applications']:
        job = next((j for j in db['jobs'] if j['id'] == app['jobId']), None)
        app_with_job = dict(app)
        app_with_job['jobTitle'] = job['title'] if job else 'Job Hata Di Gayi'
        app_with_job['department'] = job['department'] if job else '-'
        result.append(app_with_job)

    result.sort(key=lambda a: a['appliedAt'], reverse=True)

    return jsonify(result)


# ================================================================
# ROUTE 4: Application status update karo (ADMIN ONLY)
# URL: PUT /api/applications/status/<app_id>
# ================================================================
@app_bp.route('/status/<app_id>', methods=['PUT'])
@token_required
@admin_required
def update_status(app_id):
    data = request.get_json()
    status = data.get('status', '')

    # Sirf yeh 3 values allowed hain
    valid_statuses = ['Pending', 'Approved', 'Rejected']
    if status not in valid_statuses:
        return jsonify({'message': 'Status sirf Pending, Approved ya Rejected ho sakta hai.'}), 400

    db = read_db()

    # Application dhundho
    app_index = next(
        (i for i, a in enumerate(db['applications']) if a['id'] == app_id),
        None
    )

    if app_index is None:
        return jsonify({'message': 'Application nahi mili.'}), 404

    # Sirf status field update karo
    db['applications'][app_index]['status'] = status
    write_db(db)

    return jsonify({
        'message': f'Status {status} kar diya!',
        'application': db['applications'][app_index]
    })


# ================================================================
# ROUTE 5: Dashboard stats (ADMIN ONLY)
# URL: GET /api/applications/stats
# ================================================================
@app_bp.route('/stats', methods=['GET'])
@token_required
@admin_required
def get_stats():
    db = read_db()

    apps = db['applications']

    # len() = list mein kitne items hain
    # sum() = count karo jahan condition sahi ho
    stats = {
        'totalJobs': len(db['jobs']),
        'totalApplicants': sum(1 for u in db['users'] if u['role'] == 'user'),
        'totalApplications': len(apps),
        'approved': sum(1 for a in apps if a['status'] == 'Approved'),
        'pending': sum(1 for a in apps if a['status'] == 'Pending'),
        'rejected': sum(1 for a in apps if a['status'] == 'Rejected'),

        # Last 5 jobs (newest first)
        # [-5:] = list ke last 5 items lo
        # [::-1] = list ko ulta karo (reverse)
        'recentJobs': sorted(db['jobs'], key=lambda j: j['createdAt'], reverse=True)[:5],

        # Last 5 applications with job title
        'recentApplications': [
            {**a, 'jobTitle': next(
                (j['title'] for j in db['jobs'] if j['id'] == a['jobId']),
                'Hata Di Gayi'
            )}
            for a in sorted(apps, key=lambda a: a['appliedAt'], reverse=True)[:5]
        ]
        # {**a, 'jobTitle': ...} = application ki copy banao + jobTitle add karo
        # ** = dictionary ko "unpack" karo (spread operator jaisa)
    }

    return jsonify(stats)
