# ================================================================
# 📄 FILE: app.py
# 📂 FOLDER: backend/
# 🎯 YEH SABSE IMPORTANT FILE HAI!
#    Yeh pura server start karta hai.
#    Isko run karte hain: python app.py
#
# 🔤 FLASK KYA HAI?
#    Flask = Python ka web framework
#    Framework matlab: ek ready-made system jisme kaam karo
#    Jaise Express.js tha Node.js ke liye,
#    Flask wahi kaam karta hai Python ke liye
#
# 🔤 SERVER KYA HOTA HAI?
#    Server = ek program jo SUNTA hai browser ki requests ko
#    aur jawab deta hai.
#    Jaise ek dukaan — customer aata hai, order deta hai,
#    dukandaar deta hai.
#    Browser = customer, Server = dukaan, API = menu
# ================================================================

# Flask = main framework
# CORS = Cross-Origin Resource Sharing
#        Browser ko allow karna frontend se backend se baat karne ke liye
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# Hamare route files import karo
# Blueprint = mini-app jisme routes hain
from routes.auth_routes import auth_bp
from routes.job_routes import job_bp
from routes.application_routes import app_bp

# ----------------------------------------------------------------
# Flask app create karo
# __name__ = current file ka naam
# static_folder = yahan frontend ki files hain
# static_url_path = '/' = root URL pe frontend serve karo
# ----------------------------------------------------------------
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
    static_url_path=''
)

# CORS enable karo — browser ko backend se baat karne do
# Bina iske browser block kar deta hai requests
CORS(app)


# ================================================================
# BLUEPRINTS REGISTER KARO
# Matlab: in route files ke sab routes is app mein add karo
# JavaScript mein tha: app.use('/api/auth', require('./routes/auth'))
# Python mein: app.register_blueprint(auth_bp)
# ================================================================
app.register_blueprint(auth_bp)   # /api/auth/login, /api/auth/register
app.register_blueprint(job_bp)    # /api/jobs
app.register_blueprint(app_bp)    # /api/applications


# ================================================================
# FRONTEND SERVE KARO
# Jab browser koi bhi page maange jo API nahi hai,
# toh frontend ka index.html do
#
# @app.route('/') = root URL ke liye
# @app.route('/<path:path>') = koi bhi aur URL ke liye
# ================================================================
@app.route('/')
def serve_index():
    # send_from_directory = ek specific folder se file bhejo
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', 'frontend'),
        'index.html'
    )

@app.route('/<path:path>')
def serve_static(path):
    # Pehle dekhho file exist karti hai kya
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    full_path = os.path.join(frontend_dir, path)

    if os.path.exists(full_path):
        # Agar file hai toh woh bhejo
        return send_from_directory(frontend_dir, path)
    else:
        # Warna index.html bhejo (SPA routing ke liye)
        return send_from_directory(frontend_dir, 'index.html')


# ================================================================
# SERVER START KARO
# if __name__ == '__main__': = yeh sirf tab chale jab seedha
# "python app.py" run karo. Import hone pe nahi chale.
#
# app.run() = Flask server start karo
# debug=True = Agar koi error aaye toh browser mein dikhao
#              Aur server automatically restart ho jab file badlo
# port=3000  = Kaunse "darwaaze" pe suno (3000 ka matlab localhost:3000)
# host='0.0.0.0' = Sab IP addresses pe suno
#                  Matlab LAN pe doosre devices bhi access kar sakte hain
# ================================================================
if __name__ == '__main__':
    print()
    print('=' * 50)
    print('✅ Govt Job System CHALU HO GAYA!')
    print('=' * 50)
    print()
    print('🌐 Browser mein kholo: http://localhost:3000')
    print()
    print('🔑 ADMIN Login:')
    print('   Email:    admin@govtjobs.in')
    print('   Password: secret123')
    print()
    print('👤 USER Login:')
    print('   Email:    rahul@example.com')
    print('   Password: secret123')
    print()
    print('Server band karne ke liye: CTRL + C')
    print()

    app.run(debug=True, port=3000, host='0.0.0.0')
