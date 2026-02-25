import os
from datetime import datetime

import bcrypt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai import types
from pymongo import MongoClient

# Load API Key from .env file
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
CORS(app) 

# --- 1. MongoDB Setup (Local Connection) ---
# Since you just installed MongoDB locally, we use localhost
MONGO_URI = "mongodb://localhost:27017/"
db_client = MongoClient(MONGO_URI)
db = db_client.knoyosta_db
users_collection = db.users
sessions_collection = db.sessions

# --- 2. AI Setup ---
ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Mystical Predictor Persona
SYSTEM_PROMPT = """
You are knoYOsta, a legendary AI cosmic oracle and master of destiny. 
Your tone is divine, cinematic, and spiritually profound.

CORE MISSION:
When a user provides their birth date, you calculate their Sun Sign.
You must provide 'Cosmic Roadmaps'—predicting the energetic themes and life events of their upcoming year (2026).

PREDICTION STYLE:
1. Don't just give traits; give FORECASTS. (e.g., "The alignment of Saturn in March suggests a major career pivot.")
2. Focus on: Career evolution, Emotional breakthroughs, and Spiritual growth.
3. Use the year 2026 as the current timeline.
4. Maintain mystical mystery but give the user actionable wisdom.

GUARDRAILS:
- Do not predict exact dates of death or specific medical diagnoses.
- Remind users that while the stars incline, the mind directs (Free Will).
"""

# --- 3. Zodiac Logic ---
ZODIAC_DATA = {
    "Aries": {"element": "Fire", "planet": "Mars"},
    "Taurus": {"element": "Earth", "planet": "Venus"},
    "Gemini": {"element": "Air", "planet": "Mercury"},
    "Cancer": {"element": "Water", "planet": "Moon"},
    "Leo": {"element": "Fire", "planet": "Sun"},
    "Virgo": {"element": "Earth", "planet": "Mercury"},
    "Libra": {"element": "Air", "planet": "Venus"},
    "Scorpio": {"element": "Water", "planet": "Pluto"},
    "Sagittarius": {"element": "Fire", "planet": "Jupiter"},
    "Capricorn": {"element": "Earth", "planet": "Saturn"},
    "Aquarius": {"element": "Air", "planet": "Uranus"},
    "Pisces": {"element": "Water", "planet": "Neptune"}
}

def get_zodiac_sign(day, month):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19): return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20): return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20): return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22): return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22): return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22): return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22): return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21): return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21): return "Sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19): return "Capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18): return "Aquarius"
    else: return "Pisces"

# --- 4. Registration & Profile Creation ---
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    dob_str = data.get("birth_date")
    
    if not email or not password or not dob_str:
        return jsonify({"error": "Missing sacred scrolls (data)."}), 400

    if users_collection.find_one({"account.email": email}):
        return jsonify({"error": "This soul is already registered in the stars."}), 400

    # Calculate Zodiac
    birth_date = datetime.strptime(dob_str, "%Y-%m-%d")
    sign = get_zodiac_sign(birth_date.day, birth_date.month)

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user_doc = {
        "account": {"email": email, "pw_hash": hashed_pw.decode('utf-8')},
        "birth_info": {"dob": dob_str, "sign": sign},
        "created_at": datetime.utcnow()
    }
    
    users_collection.insert_one(user_doc)
    return jsonify({"message": "Profile aligned.", "sun_sign": sign}), 201

# --- 5. Predictor Chat Endpoint ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get("message")
    session_id = data.get("session_id", "default")

    # Fetch history from MongoDB
    session = sessions_collection.find_one({"session_id": session_id})
    if not session:
        session = {"session_id": session_id, "messages": []}
        sessions_collection.insert_one(session)

    # Build Prompt
    history_text = ""
    for m in session['messages'][-6:]:
        history_text += f"{m['role']}: {m['content']}\n"

    full_prompt = f"{SYSTEM_PROMPT}\n\nRecent History:\n{history_text}\nSeeker: {msg}\nknoYOsta:"

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.0-flash', # Optimized for fast, mystical responses
            contents=full_prompt
        )
        prediction = response.text

        # Update MongoDB History
        sessions_collection.update_one(
            {"session_id": session_id},
            {"$push": {"messages": {"$each": [
                {"role": "User", "content": msg},
                {"role": "knoYOsta", "content": prediction}
            ]}}}
        )

        return jsonify({"response": prediction})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)