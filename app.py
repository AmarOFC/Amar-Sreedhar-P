import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
from groq import Groq  # 🟢 Swapped Gemini for Groq

app = Flask(__name__)

# 1. OPEN THE DOOR FOR GITHUB PAGES (Fixes CORS Blocks)
CORS(app)

# 2. GET CLOUD VARIABLES FROM RENDER
MONGO_URI = os.environ.get("MONGO_URI")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") # 🟢 Look for the new Groq key

# 3. CONNECT TO MONGODB ATLAS (Fixes the localhost 500 error)
if MONGO_URI:
    try:
        db_client = MongoClient(MONGO_URI) # Renamed to db_client for safety
        db = db_client.get_database("knoyosta_db")
        users_collection = db.users
        print("Successfully connected to the Cosmic Database!")
    except Exception as e:
        print(f"Database connection failed: {e}")
else:
    print("WARNING: MONGO_URI is missing from Render Environment Variables!")

# 4. SETUP GROQ AI
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
    MODEL = "llama-3.3-70b-versatile" # 🟢 Set the ultra-fast Groq model
else:
    print("WARNING: GROQ_API_KEY is missing from Render Environment Variables!")

# --- HELPER FUNCTION: Calculate Zodiac Sign ---
def get_sun_sign(date_string):
    try:
        # Assumes date format is YYYY-MM-DD
        parts = date_string.split('-')
        month = int(parts[1])
        day = int(parts[2])
        
        if (month == 3 and day >= 21) or (month == 4 and day <= 19): return "Aries"
        if (month == 4 and day >= 20) or (month == 5 and day <= 20): return "Taurus"
        if (month == 5 and day >= 21) or (month == 6 and day <= 20): return "Gemini"
        if (month == 6 and day >= 21) or (month == 7 and day <= 22): return "Cancer"
        if (month == 7 and day >= 23) or (month == 8 and day <= 22): return "Leo"
        if (month == 8 and day >= 23) or (month == 9 and day <= 22): return "Virgo"
        if (month == 9 and day >= 23) or (month == 10 and day <= 22): return "Libra"
        if (month == 10 and day >= 23) or (month == 11 and day <= 21): return "Scorpio"
        if (month == 11 and day >= 22) or (month == 12 and day <= 21): return "Sagittarius"
        if (month == 12 and day >= 22) or (month == 1 and day <= 19): return "Capricorn"
        if (month == 1 and day >= 20) or (month == 2 and day <= 18): return "Aquarius"
        return "Pisces"
    except:
        return "Mystic"

# --- ROUTE 1: REGISTRATION ---
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        birth_date = data.get('birth_date')

        if not email or not password or not birth_date:
            return jsonify({"error": "Please provide all cosmic details."}), 400

        # Hash the password for security
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        sun_sign = get_sun_sign(birth_date)

        # Save the user to MongoDB
        users_collection.update_one(
            {"email": email},
            {"$set": {"password": hashed_pw, "birth_date": birth_date, "sun_sign": sun_sign}},
            upsert=True
        )

        # Send the sun sign back to your script.js to show on screen
        return jsonify({"sun_sign": sun_sign}), 200

    except Exception as e:
        print(f"Registration Error: {e}")
        return jsonify({"error": "The stars are misaligned. Backend error."}), 500

# --- ROUTE 2: CHAT WITH GROQ ---
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "Speak your mind, traveler."}), 400
            
        if not GROQ_API_KEY:
            return jsonify({"error": "Cosmic connection lost (Missing API Key)."}), 500

        # 🟢 Connect to Groq and get an answer using the new format
        completion = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are knoYOsta, a mystical cosmic oracle. Reply to the traveler in a short, mystical, astrological tone."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7 # Keeps the responses creative and mystical
        )
        
        # Extract the exact text from Groq's response structure
        bot_reply = completion.choices[0].message.content

        return jsonify({"response": bot_reply}), 200

    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"error": "The celestial signals are temporarily obscured."}), 500

# --- START THE SERVER ---
if __name__ == '__main__':
    # Render assigns a specific port, so we must ask the OS what it is
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
