# ================================================================
# 📄 FILE: auth.py
# 📂 FOLDER: backend/middleware/
# 🎯 YEH KYA KARTA HAI?
#    Yeh SECURITY GUARD hai hamare server ka.
#
#    Soch ek cinema hall:
#    - Ticket kharido (login karo → JWT token milta hai)
#    - Guard ticket check karta hai entry pe
#      (token_required check karta hai har protected route pe)
#    - VIP area ke liye special pass chahiye
#      (admin_required check karta hai admin hai ya nahi)
#
# 🔤 MIDDLEWARE KYA HOTA HAI?
#    Middleware = kuch code jo request aur response ke BEECH mein chalta hai
#    Jaise security check — building mein ghuste waqt
#    reception tak pahunchne se pehle
# ================================================================

# jwt = JSON Web Token library
# Isse token banate aur verify karte hain
import jwt

# functools.wraps = Python decorator ke liye zaroori
# (neeche explain kiya hai)
from functools import wraps

# Flask ke tools import karna
# request  = browser se aaya data padhne ke liye
# jsonify  = Python dict ko JSON response mein badalna
# g        = request ke dauran temporary data store karne ke liye
#            (jaise ek request ki "pocket")
from flask import request, jsonify, g

# ----------------------------------------------------------------
# SECRET KEY
# Yeh woh "stamp" hai jo tokens banane aur verify karne ke liye use hota hai
# Real projects mein yeh .env file mein hota hai
# Abhi learning ke liye yahan likha hai
# ----------------------------------------------------------------
SECRET_KEY = 'govtjobs_secret_key_2024'


# ================================================================
# DECORATOR 1: token_required
# 🎯 PURPOSE: Check karo — kya user logged in hai?
#
# 🔤 DECORATOR KYA HOTA HAI? (@wala)
#    Decorator ek special function hai jo doosre functions ke
#    upar likha jaata hai @symbol ke saath.
#    Matlab: "Yeh function chalane se PEHLE pehle yeh code chala"
#
#    Jaise:
#    @token_required          ← pehle yeh chala (check token)
#    def get_jobs():          ← phir yeh chala (jobs do)
#        return jobs
#
#    JavaScript mein hum middleware aise likhte the:
#    router.get('/', authMiddleware, getJobs)
#    Python mein hum @decorator likhte hain
# ================================================================
def token_required(f):
    # @wraps(f) = original function ka naam preserve karo
    # Technical Python requirement hai decorators ke liye
    @wraps(f)
    def decorated(*args, **kwargs):
        # *args, **kwargs = koi bhi arguments aane do
        # (kyunki har protected function alag arguments leta hai)

        # Request ke headers se token lo
        # Headers = extra information jo browser request ke saath bhejta hai
        # JavaScript mein: req.headers['authorization']
        # Python/Flask mein: request.headers.get('Authorization')
        token = request.headers.get('Authorization')

        # Agar koi token nahi aaya — matlab user logged in nahi
        # 401 = HTTP status code for "Unauthorized"
        if not token:
            return jsonify({'message': 'Token nahi mila. Pehle login karo.'}), 401

        try:
            # jwt.decode() = token verify karo aur andar ka data nikalo
            # Token mein user ka id, name, email, role store hota hai
            # algorithms=['HS256'] = encryption algorithm ka naam
            decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            # Decoded user info ko 'g' mein store karo
            # g = Flask ka global request storage
            # Iska matlab: is request ke dauran koi bhi function
            # g.current_user se user ka data padh sakta hai
            g.current_user = decoded

        except jwt.ExpiredSignatureError:
            # Token expire ho gaya (24 hours ke baad)
            return jsonify({'message': 'Token expire ho gaya. Dobara login karo.'}), 401

        except jwt.InvalidTokenError:
            # Token galat hai ya tamper kiya gaya
            return jsonify({'message': 'Invalid token. Dobara login karo.'}), 401

        # Sab check ho gaya — original function ko chalne do
        # f(*args, **kwargs) = woh actual function call karo
        # jo @token_required ke neeche likha hai
        return f(*args, **kwargs)

    return decorated


# ================================================================
# DECORATOR 2: admin_required
# 🎯 PURPOSE: Sirf ADMIN users ko allow karo
#    Yeh token_required ke BAAD use hota hai
#    Pehle check: logged in hai? (token_required)
#    Phir check: admin hai? (admin_required)
# ================================================================
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # g.current_user token_required ne set kiya tha
        # Ab check karo role admin hai ya nahi
        if g.current_user.get('role') != 'admin':
            # 403 = Forbidden (logged in hai but allowed nahi)
            return jsonify({'message': 'Access denied. Sirf admin ke liye.'}), 403

        return f(*args, **kwargs)

    return decorated
