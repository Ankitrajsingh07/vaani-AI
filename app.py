import os 
import platform
from flask import Flask, render_template, request, jsonify

from database import register_user, login_user, save_contact, save_chat
from openai import OpenAI
from flask import session
import datetime
import pytz
import requests

from dotenv import load_dotenv
load_dotenv()




 #initialize open AI client 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#create chat memory list
chat_history = []

#initialize app
app = Flask(__name__)
app.secret_key = "vaani_secret_key"

app.secret_key = os.getenv("SECRET_KEY")


#AI function

def ask_ai(prompt):
    try:
        global chat_history

        # 🔍 DEBUG: check API key
        api_key = os.getenv("OPENAI_API_KEY")
        print("API KEY FOUND:", bool(api_key))

        # Add user message
        chat_history.append({"role": "user", "content": prompt})

        # Keep last 6 messages
        chat_history = chat_history[-6:]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Vaani, a smart AI assistant."}
            ] + chat_history,
            max_tokens=100
        )

        reply = response.choices[0].message.content.strip()

        chat_history.append({"role": "assistant", "content": reply})

        return reply

    except Exception as e:
        print("🚨 AI FULL ERROR:", str(e))   # IMPORTANT
        return f"AI error: {str(e)}"

#  WEATHER FUNCTION
def get_weather(city):
    api_key = "fa8b806106ef9f83e81e91885629997b"   # 🔁 replace with your key

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        data = requests.get(url).json()

        if data.get("cod") == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"The temperature in {city} is {temp}°C with {desc}"
        else:
            return f"Error: {data.get('message')}"

    except Exception as e:
        print("Weather Error:", e)
        return "Unable to fetch weather"

#  INTENT DETECTION
def detect_intent(user_input):
    words = user_input.split()

    if any(word in ["hello", "hi", "hey"] for word in words):
        return "greeting"

    elif "time" in user_input:
        return "time"

    elif "youtube" in user_input:
        return "youtube"

    elif "google" in user_input:
        return "google"

    elif "search" in user_input:
        return "search"

    elif "weather" in user_input:
        return "weather"

    elif "gmail" in user_input:
        return "gmail"

    # calculator and notepad
    elif any(word in user_input for word in ["notepad", "text editor"]):
        return "notepad"

    elif any(word in user_input for word in ["calculator", "calc"]):
        return "calculator"
    
    elif "file explorer" in user_input or "explorer" in user_input:
        return "explorer"

    elif "file" in user_input:
        return "file"

    else:
        return "ai"

#  HOME ROUTE
@app.route("/")
def home():
    return render_template("index.html")

#register route
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    register_user(data["username"], data["password"])
    return jsonify({"message": "User registered"})


#login route
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = login_user(data["username"], data["password"])

    if user:
        session["user"] = data["username"]   # ✅ store session
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid credentials"})


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return "Logged out"

# SEND CONTACT MESSAGE ROUTE
@app.route("/contact", methods=["POST"])
def contact():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    save_contact(name, email, message)

    return jsonify({"message": "Message saved successfully"})


#  COMMAND ROUTE
@app.route("/command", methods=["POST"])
def command():
    #  PROTECT ROUTE
    if "user" not in session:
        return jsonify({"response": "Please login first"})
    
    try:
        user_input = request.json.get("message")

        if not user_input:
            return jsonify({"response": "No input received"})

        user_input = user_input.lower()

        intent = detect_intent(user_input)

        

        # INTENT HANDLING
        if intent == "greeting":
            response = "Hello Ankit!"
        
        #time

        elif intent == "time":
            ist = pytz.timezone("Asia/Kolkata")
            now = datetime.datetime.now(ist).strftime("%H:%M")
            response = f"Current time is {now}"
        
        #youtube

        elif intent == "youtube":
            response = "Opening YouTube"
            
            return jsonify({
                "response": response,
                "action": "open_url",
                "url": "https://www.youtube.com"
            })
        
        #google
        elif intent == "google":
            response = "Opening Google"
            
            return jsonify({
                "response": response,
                "action": "open_url",
                "url": "https://www.google.com"
            })
        
        #search
        elif intent == "search":
            query = user_input.replace("search", "").strip()

            if not query:
                response = "What do you want me to search?"
            else:
                response = f"Searching for {query}"
                
                return jsonify({
                    "response": response,
                    "action": "search_google",
                    "query": query
                })
            
        #gmail Action
        elif intent == "gmail":
            return jsonify({
                "response": "Opening Gmail",
                "action": "open_url",
                "url": "https://mail.google.com"
            })
        
        #File actions - only works locally
        #notepad
        elif intent == "notepad":
            try:
                if platform.system() == "Windows":
                    os.system("start notepad")
                    response = "Opening Notepad"
                else:
                    response = "Feature not available online"
            except Exception as e:
                print("Notepad Error:", e)
                response = "Failed to open Notepad"
        
        #calculator
        elif intent == "calculator":
            try:
                if platform.system() == "Windows":
                    os.system("start calc")
                    response = "Opening Calculator"
                else:
                    response = "Feature not available online"
            except Exception as e:
                print("Calculator Error:", e)
                response = "Failed to open Calculator"
        

        elif intent == "file":
            os.startfile("C:\\Users\\HP\\Desktop\\file.txt")
            response = "Opening file"

        elif "chrome" in user_input:
            os.system("start chrome")
            response = "Opening Chrome"

       #file explorer part
        elif intent == "explorer":
            try:
                # import platform

                if platform.system() == "Windows":
                    os.system("start explorer")
                    response = "Opening File Explorer"
                else:
                    response = "File Explorer is only available on Windows"

            except Exception as e:
                print("Explorer Error:", e)
                response = "Failed to open File Explorer"
        

        #weather part

        elif intent == "weather":
            words = user_input.split()

            if "in" in words:
                city = words[words.index("in") + 1]
                city = city.capitalize() + ",IN"
            else:
                city = "Pune,IN"

            response = get_weather(city)

        else:
            response = ask_ai(user_input)

        # 💾 SAVE CHAT
        

        return jsonify({"response": response})

    except Exception as e:
        print("Error:", e)
        return jsonify({"response": "Error occurred"})

# ▶ RUN APP
if __name__ == "__main__":
    app.run()