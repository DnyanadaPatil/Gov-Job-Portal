# 🏛️ Government Job Management System
## Python (Flask) Version — AIML Students Ke Liye!

---

## 📁 FOLDER STRUCTURE (Kahan kya hai)

```
govt-job-python/
│
├── frontend/                    ← Browser mein dikhne wali cheezein
│   ├── index.html               ← Login page
│   ├── register.html            ← Register page
│   ├── pages/
│   │   └── dashboard.html       ← Main app (sab pages ek file mein)
│   ├── css/
│   │   └── style.css            ← Saari styling (colors, layout)
│   └── js/
│       └── app.js               ← Frontend JavaScript
│
└── backend/                     ← Python server (tumhara wala!)
    ├── app.py                   ← ⭐ MAIN FILE — yahi run karo!
    ├── requirements.txt         ← Packages ki list (pip install ke liye)
    │
    ├── routes/                  ← URL paths
    │   ├── auth_routes.py       ← /api/auth/login, /register
    │   ├── job_routes.py        ← /api/jobs
    │   └── application_routes.py ← /api/applications
    │
    ├── middleware/
    │   └── auth.py              ← Security (token check karta hai)
    │
    └── data/
        ├── db.json              ← Humara "database" (JSON file)
        └── db.py                ← db.json padhne/likhne ke functions
```

---

## 🔤 Node.js → Python Kya Badla?

| Node.js (Pehle) | Python Flask (Ab) | Kaam |
|-----------------|-------------------|------|
| `const express = require('express')` | `from flask import Flask` | Server banao |
| `app.use(cors())` | `CORS(app)` | Browser ko allow karo |
| `app.get('/route', fn)` | `@app.route('/route')` | Route banana |
| `req.body` | `request.get_json()` | Request data padhna |
| `res.json({})` | `jsonify({})` | JSON response bhejna |
| `npm install` | `pip install -r requirements.txt` | Packages install karo |
| `node app.js` | `python app.py` | Server start karo |
| `router.use(middleware)` | `@decorator` | Middleware use karo |
| `JSON.parse()` | `json.load()` | JSON padhna |
| `JSON.stringify()` | `json.dump()` | JSON likhna |

---

## 🚀 PROJECT KAISE CHALAYEIN — Ek Ek Step

### Step 1: Python Install Karo

Python already installed hai AIML ke students ke liye!
Check karo:
```
python --version
```
Ya:
```
python3 --version
```
Kuch dikhna chahiye jaise: `Python 3.11.0` ✅

Nahi dikha? https://python.org se download karo.

---

### Step 2: ZIP Extract Karo

Download kiya hua ZIP extract karo — Desktop pe rakhna easy hoga.
Folder ka naam: `govt-job-python`

---

### Step 3: Terminal/Command Prompt Kholo

**Windows:**
- Windows key dabaao → `cmd` likho → Enter

**Mac:**
- Cmd + Space → `Terminal` likho → Enter

---

### Step 4: Backend Folder Mein Jao

**Windows:**
```
cd Desktop\govt-job-python\backend
```

**Mac/Linux:**
```
cd ~/Desktop/govt-job-python/backend
```

---

### Step 5: Virtual Environment Banao (Recommended!)

🔤 **Virtual Environment kya hai?**
Ek alag jagah jahan sirf is project ke packages install hote hain.
Tumhare system ke Python ko affect nahi karta.

```
python -m venv venv
```

Virtual environment activate karo:

**Windows:**
```
venv\Scripts\activate
```

**Mac/Linux:**
```
source venv/bin/activate
```

Terminal mein `(venv)` dikhna chahiye — matlab active hai ✅

---

### Step 6: Packages Install Karo

```
pip install -r requirements.txt
```

Yeh download karega:
- flask (web server)
- flask-cors (browser allow)
- bcrypt (password security)
- pyjwt (token banao)

⏱️ 1-2 minute lagega. Normal hai!

---

### Step 7: Passwords Fix Karo (Ek baar karna hai!)

db.json mein passwords bcrypt se hashed hain.
Default password `secret123` hai sabke liye.

Agar naye hashed passwords chahiye, yeh script chalao:

```python
# Terminal mein python likho phir yeh paste karo:
import bcrypt
pw = bcrypt.hashpw('secret123'.encode(), bcrypt.gensalt()).decode()
print(pw)
# Output copy karo aur db.json mein sab "password" fields mein paste karo
```

---

### Step 8: Server Start Karo!

```
python app.py
```

Yeh dikhega:
```
==================================================
✅ Govt Job System CHALU HO GAYA!
==================================================

🌐 Browser mein kholo: http://localhost:3000
```

---

### Step 9: Browser Mein Kholo

Browser mein jao: **http://localhost:3000**

Login karo:
- Admin: `admin@govtjobs.in` / `secret123`
- User: `rahul@example.com` / `secret123`

---

## 🛑 Server Band Karo

Terminal mein: **Ctrl + C**

---

## ❓ Common Problems

**Problem: "ModuleNotFoundError: No module named 'flask'"**
Solution: `pip install -r requirements.txt` phir se chalao

**Problem: "Port 3000 already in use"**
Solution: `app.py` mein `port=3000` ko `port=3001` kar do
Browser mein `http://localhost:3001` kholo

**Problem: Passwords kaam nahi kar rahe**
Solution: Step 7 wali script chalao — naye hashed passwords banao

**Problem: "python command not found"**
Solution: `python3 app.py` try karo (Mac/Linux pe)

---

## 🎓 AIML Ke Liye Extra — Kya Aur Seekh Sakte Ho?

Kyunki tum AIML ke ho, aage yeh kar sakte ho:

1. **SQLite ya PostgreSQL**: JSON file ki jagah real database
2. **ML Model Integration**: Resume screening feature
   - Users ka resume analyze karo
   - Job ke liye suitable hai ya nahi check karo
3. **FastAPI**: Flask se faster, modern Python web framework
4. **Docker**: Project ko container mein pack karo
5. **Deployment**: Railway.app ya Render.com pe FREE deploy karo

---

Shabash bhai! Python mein website bana li! 🎉🐍
