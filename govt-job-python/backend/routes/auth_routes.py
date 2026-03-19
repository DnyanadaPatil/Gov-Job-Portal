# ================================================================
# 📄 FILE: auth_routes.py
# 📂 FOLDER: backend/routes/
# 🎯 YEH KYA KARTA HAI?
#    Yeh LOGIN aur REGISTER ke URL routes handle karta hai.
#
# 🔤 ROUTE KYA HOTA HAI?
#    Route = URL path + HTTP method + function ka connection
#
#    Example:
#    POST /api/auth/login → login() function call hoga
#    POST /api/auth/register → register() function call hoga
#
# 🔤 BLUEPRINT KYA HOTA HAI?
#    Flask mein Blueprint = ek mini-app jiska apna URL prefix hota hai
#    Jaise routes ko folders mein organize karna
#    Hum banate hain: Blueprint('auth', prefix='/api/auth')
#    Matlab is file ke sab routes /api/auth/ se start honge
# ================================================================

# Flask tools import karo
# Blueprint = routes organize karne ka tarika
# request   = browser se aaya data
# jsonify   = Python dict → JSON response
from flask import Blueprint, request, jsonify

# Security tools
import bcrypt   # Password hash karne ke liye
import jwt      # Token banane ke liye
import uuid     # Unique ID banane ke liye
from datetime import datetime, timedelta, timezone  # Time ke liye

# Hamare database helper functions
from data.db import read_db, write_db

# Secret key middleware se import karo
from middleware.auth import SECRET_KEY

# ----------------------------------------------------------------
# Blueprint banana
# 'auth'       = is blueprint ka naam
# __name__     = current file ka naam (Python ka convention)
# url_prefix   = sab routes iske aage se start honge
# ----------------------------------------------------------------
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ================================================================
# ROUTE 1: REGISTER
# URL: POST /api/auth/register
#
# 🔤 @auth_bp.route() KYA HAI?
#    Yeh ek DECORATOR hai jo batata hai:
#    "Jab browser /register pe POST request bheje,
#     toh register() function chala"
#
#    methods=['POST'] = sirf POST requests allow karo
#    (GET requests yahan nahi aayengi)
# ================================================================
@auth_bp.route('/register', methods=['POST'])
def register():
    # --------------------------------------------------------
    # 🔤 request.get_json() KYA KARTA HAI?
    #    Browser ne JSON format mein data bheja:
    #    {"name": "Rahul", "email": "r@r.com", "password": "abc"}
    #    request.get_json() us JSON ko Python dictionary mein badal deta hai
    #    JavaScript mein req.body tha
    # --------------------------------------------------------
    data = request.get_json()

    # Dictionary se values nikalo
    # .get('name') = 'name' key ki value lo
    # Agar key nahi hai toh None return hogi (crash nahi hoga)
    name = data.get('name', '').strip()       # .strip() = spaces hatao
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # Validation: sab fields bhare hone chahiye
    # 'not name' = name empty hai ya nahi
    if not name or not email or not password:
        # jsonify() = Python dict ko JSON response mein badlo
        # 400 = Bad Request (user ne galat ya incomplete data bheja)
        return jsonify({'message': 'Sab fields bharo.'}), 400

    # Database padho
    db = read_db()

    # Check karo: kya yeh email pehle se registered hai?
    # next() = list mein se pehla matching item nikalo
    # (u for u in db['users'] if u['email'] == email) = generator
    # None = agar koi nahi mila toh None do
    existing = next((u for u in db['users'] if u['email'] == email), None)
    if existing:
        return jsonify({'message': 'Yeh email pehle se registered hai.'}), 400

    # --------------------------------------------------------
    # PASSWORD HASH KARO (scramble for security)
    # bcrypt.hashpw() = password ko scramble karo
    # password.encode('utf-8') = string ko bytes mein badlo
    #   (bcrypt bytes chahta hai, string nahi)
    # bcrypt.gensalt() = random "salt" banao (extra security ke liye)
    # .decode('utf-8') = bytes ko wapas string mein badlo (storage ke liye)
    # --------------------------------------------------------
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Naya user object banao
    # str(uuid.uuid4()) = random unique ID banao jaise "a3b2-c1d4-..."
    new_user = {
        'id': str(uuid.uuid4()),
        'name': name,
        'email': email,
        'password': hashed_pw,      # Scrambled password save karo, real nahi!
        'role': 'user',             # Naye users hamesha 'user' hote hain, 'admin' nahi
        'createdAt': datetime.now(timezone.utc).isoformat()  # Current time
    }

    # User ko list mein add karo
    # .append() = list ke end mein item add karo
    # JavaScript mein .push() tha
    db['users'].append(new_user)

    # Updated database save karo
    write_db(db)

    # Success response bhejo
    # 201 = Created (kuch naya bana)
    return jsonify({'message': 'Registration ho gaya! Ab login karo.'}), 201


# ================================================================
# ROUTE 2: LOGIN
# URL: POST /api/auth/login
#
# Flow:
# 1. Email aur password aaya
# 2. Database mein email se user dhundho
# 3. Password check karo (bcrypt se)
# 4. Sahi hua toh JWT token banao
# 5. Token wapas bhejo
# ================================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'message': 'Email aur password dono chahiye.'}), 400

    db = read_db()

    # Email se user dhundho
    user = next((u for u in db['users'] if u['email'] == email), None)

    # Agar user nahi mila
    if not user:
        # Security tip: yeh mat batao ki email galat hai ya password
        # Warna hacker samajh jaata hai ki email to sahi hai!
        return jsonify({'message': 'Email ya password galat hai.'}), 400

    # --------------------------------------------------------
    # PASSWORD CHECK KARO
    # bcrypt.checkpw() = typed password ko stored hash se compare karo
    # password.encode('utf-8') = string → bytes
    # user['password'].encode('utf-8') = stored hash → bytes
    # Returns True agar match hua, False agar nahi
    # --------------------------------------------------------
    password_matches = bcrypt.checkpw(
        password.encode('utf-8'),
        user['password'].encode('utf-8')
    )

    if not password_matches:
        return jsonify({'message': 'Email ya password galat hai.'}), 400

    # --------------------------------------------------------
    # JWT TOKEN BANAO
    # jwt.encode() = token banao
    # Pehla argument = token ke andar kya store karna hai (payload)
    # SECRET_KEY = hamaara secret stamp
    # algorithm='HS256' = encryption method
    # --------------------------------------------------------
    token_payload = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role'],
        # Token 24 ghante baad expire hoga
        # timedelta(hours=24) = 24 ghante add karo aaj ki date mein
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }

    token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')

    # Token aur user info wapas bhejo
    # Password kabhi nahi bhejna — security!
    return jsonify({
        'message': 'Login ho gaya!',
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }
    })
