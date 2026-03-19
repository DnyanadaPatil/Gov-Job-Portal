# ================================================================
# 📄 FILE: db.py
# 📂 FOLDER: backend/data/
# 🎯 YEH KYA KARTA HAI?
#    Yeh hamare "database helper" hai.
#    Sirf 2 kaam karta hai:
#    1. read_db()  → db.json se data padhna (READ)
#    2. write_db() → db.json mein data save karna (WRITE)
#
# 🔤 PYTHON WORDS EXPLAINED:
#    import   = kisi aur file ya tool ko load karna
#               jaise Node.js mein require() tha
#    json     = Python ka built-in tool JSON ke liye
#    os       = Python ka built-in tool file paths ke liye
#    def      = function banana ka tarika Python mein
#               (JavaScript mein "function" likhte the)
#    return   = function se result wapas bhejna
# ================================================================

# 'json' module - JSON file padhne aur likhne ke liye
# Python mein yeh already built-in hai, install nahi karna
import json

# 'os' module - file ka path dhundhne ke liye
# Windows pe C:\folder\file.json hota hai
# Mac/Linux pe /folder/file.json hota hai
# os.path.join() dono ke liye sahi path banata hai
import os

# ----------------------------------------------------------------
# DB_PATH = db.json file ka address
#
# __file__        = yeh current file (db.py) ka path hai
# os.path.dirname = us file ka folder dhundho
# os.path.join    = folder + filename jodo
#
# Result: "C:/Users/.../backend/data/db.json" jaisa kuch
# ----------------------------------------------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), 'db.json')


# ================================================================
# FUNCTION 1: read_db()
# 🎯 PURPOSE: db.json file se saara data padhna
#
# 🔤 def = "define" — isse function banate hain
#    Python mein function aise banta hai:
#        def function_name():
#            kaam karo
#            return result
#
#    JavaScript mein tha:
#        function functionName() {
#            kaam karo
#            return result
#        }
# ================================================================
def read_db():
    # 'with open(...)' = file safely kholna
    # Jaise ek drawer kholna, kaam karna, phir band karna
    # 'r' = "read mode" sirf padhna hai, likhna nahi
    # encoding='utf-8' = Hindi/Urdu/special characters ke liye
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        # json.load(f) = file ki JSON text ko
        # Python dictionary mein convert karo
        # JavaScript mein JSON.parse() tha
        return json.load(f)


# ================================================================
# FUNCTION 2: write_db(data)
# 🎯 PURPOSE: data ko wapas db.json mein save karna
#
# 🔤 'data' = parameter (jo value function mein pass karte hain)
#    Jaise ek dabba dena librarian ko — woh shelf pe rakh deta hai
# ================================================================
def write_db(data):
    # 'w' = "write mode" — file mein likhna hai
    # Agar file pehle se hai toh overwrite ho jaayegi
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        # json.dump(data, f) = Python dictionary ko
        # JSON text mein convert karke file mein likho
        # JavaScript mein JSON.stringify() tha
        # indent=2 = JSON ko sundar readable format mein likho
        json.dump(data, f, indent=2, ensure_ascii=False)
