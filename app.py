from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, LoginLog, Order, Purchase
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from ai_modules.pipeline import generate_prediction

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
client = None
if OPENROUTER_API_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")


app = Flask(__name__)
app.secret_key = 'navaratna_secret_cosmic_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

GEM_PRICES = {
    "Ruby": 500,
    "Pearl": 300,
    "Red Coral": 400,
    "Emerald": 450,
    "Yellow Sapphire": 600,
    "Diamond": 1200,
    "Blue Sapphire": 700,
    "Hessonite": 350,
    "Cat's Eye": 500,
    "Cat Eye": 500
}

# Removed safe_ollama_chat

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            
            # Create a new LoginLog entry
            log_entry = LoginLog(email=email, login_time=datetime.now())
            db.session.add(log_entry)
            db.session.commit()
            
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Email already exists', 'error')
            return redirect(url_for('signup'))
            
        hashed_password = generate_password_hash(password)
        
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            created_at=datetime.now()
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/add_purchase', methods=['POST'])
def add_purchase():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'})
        
    data = request.json
    gem_name = data.get('gem_name')
    price = data.get('price')
    
    if not gem_name or not price:
        return jsonify({'status': 'error', 'message': 'Invalid data'})
        
    purchase = Purchase(
        user_id=session['user_id'],
        gem_name=gem_name,
        price=price,
        purchase_date=datetime.utcnow()
    )
    db.session.add(purchase)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Purchase added successfully'})

@app.route('/get_history', methods=['GET'])
def get_history():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'User not logged in'})
        
    purchases = Purchase.query.filter_by(user_id=session['user_id']).order_by(Purchase.purchase_date.desc()).all()
    
    history = []
    for p in purchases:
        history.append({
            'gem_name': p.gem_name,
            'price': p.price,
            'date': p.purchase_date
        })
        
    return jsonify({'status': 'success', 'history': history})

@app.route('/calculate-price', methods=['POST'])
def calculate_price():
    data = request.json
    gemstone = data.get('gemstone')
    weight = data.get('weight')
    
    try:
        weight = float(weight)
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "Invalid weight"}), 400
        
    if weight <= 0:
        return jsonify({"status": "error", "message": "Weight must be > 0"}), 400
        
    price_per_gram = GEM_PRICES.get(gemstone, 100)
    total_price = price_per_gram * weight
    
    return jsonify({
        "status": "success",
        "total_price": total_price
    })

@app.route('/place-order', methods=['POST'])
def place_order():
    try:
        if request.is_json:
            data = request.json
            gemstone = data.get('gemstone')
            weight = data.get('weight')
            name = data.get('name')
            address = data.get('address')
        else:
            gemstone = request.form.get('gemstone')
            weight = request.form.get('weight')
            name = request.form.get('name')
            address = request.form.get('address')
            
        try:
            weight = float(weight)
        except:
            weight = 0.0
            
        if weight <= 0:
            return jsonify({'status': 'error', 'message': 'Weight must be > 0'})
            
        if not name or not name.strip():
            return jsonify({'status': 'error', 'message': 'Name cannot be empty'})
            
        if not address or not address.strip():
            return jsonify({'status': 'error', 'message': 'Address cannot be empty'})
            
        price_per_gram = GEM_PRICES.get(gemstone, 100)
        total_price = price_per_gram * weight
            
        print("Order saved:", gemstone, weight, total_price)
        
        new_order = Order(
            user_email=session.get('user_email', 'guest'),
            gemstone=gemstone,
            weight=weight,
            price=total_price,
            name=name,
            address=address,
            created_at=datetime.now()
        )
        db.session.add(new_order)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'status': 'success', 'price': total_price, 'qr_code': '/static/assets/payment_qr.png', 'message': 'Order placed successfully. Complete payment using QR.'})
        else:
            flash('Order placed successfully. Complete payment using QR.', 'success')
            return redirect(url_for('index'))
    except Exception as e:
        print("Error in /place-order:", e)
        return jsonify({'status': 'error', 'message': 'Something went wrong'}), 500

@app.route('/ai_prediction', methods=['POST'])
def ai_prediction():
    if 'user_id' not in session:
        print("--- DEBUG: Unauthorized chatbot access attempt blocked ---")
        return jsonify({"error": "Unauthorized. Please login first.", "redirect": "/login"}), 401
        
    print(f"--- DEBUG: Authenticated user accessing chatbot: {session.get('user_email')} ---")
    
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    if data.get("reset"):
        session['chat_stage'] = 1
        session['user_data'] = {}
        session['chat_history'] = []
        return jsonify({"reply": "Session reset."})

    user_message = data.get("user_message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please say something."})
        
    if 'chat_stage' not in session:
        session['chat_stage'] = 1
        session['user_data'] = {}
        
    stage = session['chat_stage']
    user_data = session.get('user_data', {})
    
    reply = ""
    recommended_gemstone = None
    
    print(f"--- DEBUG: Current conversation stage: {stage} ---")
    
    if stage == 1:
        if not re.match(r'^[A-Za-z\s]{2,50}$', user_message):
            return jsonify({"reply": "Please enter a valid name (letters only)."})
        user_data['name'] = user_message
        session['chat_stage'] = 2
        reply = f"Nice to meet you, {user_message}. <br><br><b>Step 2 of 5:</b> What is your age?"
        
    elif stage == 2:
        if not user_message.isdigit() or not (1 <= int(user_message) <= 120):
            return jsonify({"reply": "Please enter a valid age (numbers only)."})
        user_data['age'] = user_message
        session['chat_stage'] = 3
        reply = "Thank you. <br><br><b>Step 3 of 5:</b> What is your gender? (Male/Female/Other)"
        
    elif stage == 3:
        gender = user_message.strip().lower()
        if gender not in ['male', 'female', 'other']:
            return jsonify({"reply": "Please enter a valid gender (Male, Female, or Other)."})
        user_data['gender'] = gender.capitalize()
        session['chat_stage'] = 4
        reply = "Great. <br><br><b>Step 4 of 5:</b> What is your Date of Birth? (e.g., DD/MM/YYYY)"
        
    elif stage == 4:
        if not re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{4}$', user_message):
            return jsonify({"reply": "Please enter a valid date of birth (e.g., DD/MM/YYYY)."})
        user_data['dob'] = user_message
        session['chat_stage'] = 6
        reply = "Thank you. I have aligned your cosmic details. <br><br><b>Step 5 of 5:</b> What guidance or issue are you seeking today? (e.g., love, career, health, gemstone recommendation, numerology guidance)"
        
    elif stage == 6:
        user_data['problem'] = user_message
        session['chat_stage'] = 7
        
        # Calculate using existing Python pipeline
        try:
            print("--- DEBUG: Running Python logic for astrology/numerology ---")
            prediction_result = generate_prediction(
                name=user_data.get('name', ''),
                dob=user_data.get('dob', ''),
                gender=user_data.get('gender', ''),
                weight='60', # dummy weight
                zodiac='', # will be calculated
                problem=user_data.get('problem', '')
            )
            
            user_data['prediction_result'] = prediction_result
            recommended_gemstone = prediction_result.get('recommended_gemstone')
            
            # Use OpenRouter to explain the prediction
            print("--- DEBUG: OpenRouter API status: Initiating generation request ---")
            
            system_prompt = """You are Navaratna AI, a specialized premium astrology, gemstone, and numerology assistant for the Navaratna platform.
            
STRICT RULES:
1. You MUST ONLY discuss astrology, gemstones, numerology, zodiac, spiritual guidance, birth chart related suggestions, gemstone recommendations, and Navaratna-related topics.
2. If the user asks about unrelated topics (e.g., geography, politics, coding, science, random general knowledge, math, history), you MUST politely redirect them EXACTLY like this: "I specialize in astrology, gemstones, numerology, and spiritual guidance through Navaratna AI. Please ask questions related to these topics." DO NOT answer unrelated questions directly.
3. Always recommend gemstones from our platform.
4. Maintain a premium, empathetic, and spiritual astrology-focused tone.
5. Keep your responses concise and optimized for fast reading.
"""

            user_prompt = f"""
User Context:
Name: {user_data.get('name')}
Age: {user_data.get('age')}
Gender: {user_data.get('gender')}
DOB: {user_data.get('dob')}
Problem: {user_data.get('problem')}

Calculated Results:
Life Path Number: {prediction_result.get('life_path_number')}
Zodiac Sign: {prediction_result.get('zodiac_sign')}
Dominant Planet: {prediction_result.get('dominant_planet')}
Recommended Gemstone: {prediction_result.get('recommended_gemstone')}

Instructions:
Generate a personalized, empathetic, and spiritual explanation based on these results.
Include:
1. Future guidance tailored to their problem.
2. The exact recommended gemstone and how it will help.
3. Numerology insights based on their life path number.
Do not mention any AI models or how you calculated it. Keep it concise.
"""
            try:
                response = client.chat.completions.create(
                    model=OPENROUTER_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                reply = response.choices[0].message.content
                print("--- DEBUG: OpenRouter response success ---")
                
                # Initialize chat history for further conversation
                session['chat_history'] = [
                    {"role": "user", "content": f"My name is {user_data.get('name')}. I am {user_data.get('age')} years old, {user_data.get('gender')}. My DOB is {user_data.get('dob')}. I need guidance on: {user_data.get('problem')}"},
                    {"role": "assistant", "content": reply}
                ]
            except Exception as e:
                print("--- DEBUG: OpenRouter API FAILURE ---")
                print("Actual OpenRouter API error:", str(e))
                reply = "AI service is temporarily unavailable. Please try again shortly."
                session['chat_stage'] = 6 # revert stage to try again
        except Exception as e:
            print("--- DEBUG: Pipeline Logic ERROR ---")
            print("Pipeline error:", str(e))
            reply = "There was an error processing your cosmic details. Please try again with valid information."
            session['chat_stage'] = 6
            
    elif stage == 7:
        if 'chat_history' not in session:
            session['chat_history'] = []
            
        history = session['chat_history']
        
        system_prompt = """You are Navaratna AI, a specialized premium astrology, gemstone, and numerology assistant for the Navaratna platform.
        
STRICT RULES:
1. You MUST ONLY discuss astrology, gemstones, numerology, zodiac, spiritual guidance, birth chart related suggestions, gemstone recommendations, and Navaratna-related topics.
2. If the user asks about unrelated topics (e.g., geography, politics, coding, science, random general knowledge, math, history), you MUST politely redirect them EXACTLY like this: "I specialize in astrology, gemstones, numerology, and spiritual guidance through Navaratna AI. Please ask questions related to these topics." DO NOT answer unrelated questions directly.
3. Always recommend gemstones from our platform.
4. Maintain a premium, empathetic, and spiritual astrology-focused tone.
5. Keep your responses concise and optimized for fast reading.
"""
        
        # Build history for OpenRouter
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
        try:
            print("--- DEBUG: OpenRouter API status: Initiating chat message ---")
            
            messages.append({"role": "user", "content": user_message})
            
            response = client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=messages
            )
            reply = response.choices[0].message.content
            print("--- DEBUG: OpenRouter response success ---")
            
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": reply})
            session['chat_history'] = history[-10:]
            
        except Exception as e:
            print("--- DEBUG: OpenRouter API FAILURE ---")
            print("Actual OpenRouter API error:", str(e))
            reply = "AI service is temporarily unavailable. Please try again shortly."
            
    session['user_data'] = user_data
    session.modified = True
    
    return jsonify({"reply": reply, "recommended_gemstone": recommended_gemstone})

if __name__ == '__main__':
    app.run(debug=True)