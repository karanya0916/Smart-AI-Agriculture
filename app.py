import os
import json
import hashlib
import joblib
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename

import database

# Initialize Flask App
app = Flask(__name__)
app.secret_key = 'agripulse_hackathon_super_secret_key_2026'

# Ensure required directories
UPLOAD_FOLDER = os.path.join('static', 'uploads')
AUDIO_CACHE_FOLDER = os.path.join('static', 'audio_cache')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_CACHE_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_CACHE_FOLDER'] = AUDIO_CACHE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Initialize SQLite database
database.init_db()

# Global Model References
crop_model = None
fert_model = None
le_soil = None
le_crop = None
le_fert = None
disease_model = None
disease_classes = []
disease_info = {}
chatbot_kb = {}
voice_kb = {}

# 1. Load Crop Recommendation Model
try:
    if os.path.exists('models/crop_model.pkl'):
        crop_model = joblib.load('models/crop_model.pkl')
        print("Loaded models/crop_model.pkl successfully.")
except Exception as e:
    print(f"Warning: Could not load crop_model.pkl: {e}")

# 2. Load Fertilizer Recommendation Model & Encoders
try:
    if os.path.exists('models/fertilizer_model.pkl'):
        fert_model = joblib.load('models/fertilizer_model.pkl')
        le_soil = joblib.load('models/soil_encoder.pkl')
        le_crop = joblib.load('models/crop_fert_encoder.pkl')
        le_fert = joblib.load('models/fert_encoder.pkl')
        print("Loaded fertilizer models & encoders successfully.")
except Exception as e:
    print(f"Warning: Could not load fertilizer models: {e}")

# 3. Load Plant Disease Detection Model (TensorFlow / Keras)
try:
    if os.path.exists('models/plant_disease_model.keras'):
        from tensorflow.keras.models import load_model
        disease_model = load_model('models/plant_disease_model.keras')
        print("Loaded models/plant_disease_model.keras successfully.")
except Exception as e:
    print(f"Warning: Could not load plant_disease_model.keras: {e}")

# Load Disease Classes & Agronomic Metadata
try:
    if os.path.exists('models/disease_classes.json'):
        with open('models/disease_classes.json', 'r') as f:
            disease_classes = json.load(f)
    if os.path.exists('data/disease_info.json'):
        with open('data/disease_info.json', 'r') as f:
            disease_info = json.load(f)
except Exception as e:
    print(f"Warning loading disease metadata: {e}")

# 4. Load Chatbot Knowledge Base
try:
    if os.path.exists('data/chatbot_kb.json'):
        with open('data/chatbot_kb.json', 'r') as f:
            chatbot_kb = json.load(f)
except Exception as e:
    print(f"Warning loading chatbot knowledge base: {e}")

# 5. Load Multilingual Voice Knowledge Base
try:
    if os.path.exists('data/voice_multilingual_kb.json'):
        with open('data/voice_multilingual_kb.json', 'r', encoding='utf-8') as f:
            voice_kb = json.load(f)
        print("Loaded multilingual voice knowledge base successfully.")
except Exception as e:
    print(f"Warning loading multilingual voice knowledge base: {e}")

# --- Weather Intelligence Service Helper ---
CITIES_WEATHER = {
    'Karnal': {'temp': 24.5, 'humidity': 62, 'wind': 11, 'condition': 'Partly Cloudy', 'icon': '⛅', 'rain_prob': 15},
    'Ludhiana': {'temp': 23.8, 'humidity': 65, 'wind': 12, 'condition': 'Sunny', 'icon': '☀️', 'rain_prob': 10},
    'Pune': {'temp': 28.2, 'humidity': 54, 'wind': 14, 'condition': 'Clear Sky', 'icon': '☀️', 'rain_prob': 5},
    'Nagpur': {'temp': 31.0, 'humidity': 48, 'wind': 16, 'condition': 'Sunny & Warm', 'icon': '☀️', 'rain_prob': 5},
    'Varanasi': {'temp': 26.0, 'humidity': 68, 'wind': 9, 'condition': 'Scattered Clouds', 'icon': '⛅', 'rain_prob': 25},
    'Hyderabad': {'temp': 29.5, 'humidity': 56, 'wind': 15, 'condition': 'Partly Cloudy', 'icon': '⛅', 'rain_prob': 20},
    'Indore': {'temp': 27.4, 'humidity': 52, 'wind': 13, 'condition': 'Clear Sky', 'icon': '☀️', 'rain_prob': 10}
}

def get_agro_weather(city='Karnal'):
    base = CITIES_WEATHER.get(city, CITIES_WEATHER['Karnal'])
    forecast = [
        {'day': 'Today', 'high': round(base['temp'] + 2, 1), 'low': round(base['temp'] - 8, 1), 'rain': 0, 'condition': base['condition'], 'icon': base['icon']},
        {'day': 'Tomorrow', 'high': round(base['temp'] + 1, 1), 'low': round(base['temp'] - 7, 1), 'rain': 4.5, 'condition': 'Light Showers', 'icon': '🌦️'},
        {'day': 'Day 3', 'high': round(base['temp'] - 1, 1), 'low': round(base['temp'] - 8, 1), 'rain': 12.0, 'condition': 'Moderate Rain', 'icon': '🌧️'},
        {'day': 'Day 4', 'high': round(base['temp'] + 0.5, 1), 'low': round(base['temp'] - 6.5, 1), 'rain': 2.0, 'condition': 'Cloudy', 'icon': '⛅'},
        {'day': 'Day 5', 'high': round(base['temp'] + 2.5, 1), 'low': round(base['temp'] - 7, 1), 'rain': 0, 'condition': 'Clear & Sunny', 'icon': '☀️'}
    ]
    return {'current': base, 'forecast': forecast}

# --- Flask Routes ---

@app.route('/')
def dashboard():
    stats = database.get_dashboard_stats()
    return render_template('index.html', stats=stats)

@app.route('/crop', methods=['GET', 'POST'])
def crop_recommend():
    prediction = None
    form_data = None
    if request.method == 'POST':
        try:
            n = float(request.form.get('nitrogen', 80))
            p = float(request.form.get('phosphorus', 48))
            k = float(request.form.get('potassium', 40))
            ph = float(request.form.get('ph', 6.5))
            temp = float(request.form.get('temperature', 24.5))
            hum = float(request.form.get('humidity', 80))
            rain = float(request.form.get('rainfall', 210))

            form_data = {
                'nitrogen': n, 'phosphorus': p, 'potassium': k,
                'ph': ph, 'temperature': temp, 'humidity': hum, 'rainfall': rain
            }

            if crop_model:
                features = np.array([[n, p, k, temp, hum, ph, rain]])
                probs = crop_model.predict_proba(features)[0]
                best_idx = np.argmax(probs)
                best_crop = crop_model.classes_[best_idx]
                confidence = float(probs[best_idx])

                prediction = {
                    'crop': best_crop,
                    'confidence': confidence
                }

                # Log to database
                database.log_crop_prediction(n, p, k, temp, hum, ph, rain, best_crop, confidence)
                flash(f"Crop evaluation completed: {best_crop.title()} identified with {confidence*100:.1f}% confidence.", "success")
            else:
                flash("Model artifact not ready. Please train crop model first.", "error")
        except Exception as e:
            flash(f"Error evaluating crop suitability: {str(e)}", "error")

    return render_template('crop.html', prediction=prediction, form_data=form_data)

@app.route('/disease', methods=['GET', 'POST'])
def disease_detect():
    result = None
    uploaded_image_url = None

    if request.method == 'POST':
        try:
            sample_path = request.form.get('sample_path')
            file = request.files.get('leaf_image')
            target_filepath = None

            if file and file.filename != '':
                filename = secure_filename(file.filename)
                target_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(target_filepath)
                uploaded_image_url = url_for('static', filename=f'uploads/{filename}')
            elif sample_path:
                # Remove leading static/ if present
                clean_path = sample_path.replace('/static/', '').replace('static/', '')
                target_filepath = os.path.join('static', clean_path)
                uploaded_image_url = sample_path

            if target_filepath and os.path.exists(target_filepath):
                # Preprocess image for TensorFlow CNN
                img = Image.open(target_filepath).convert('RGB')
                img_resized = img.resize((128, 128))
                arr = np.array(img_resized, dtype=np.float32) / 255.0
                tensor_input = np.expand_dims(arr, axis=0)

                if disease_model and disease_classes:
                    preds = disease_model.predict(tensor_input, verbose=0)[0]
                    best_idx = int(np.argmax(preds))
                    pred_class = disease_classes[best_idx]
                    confidence = float(preds[best_idx])

                    # Fetch agronomic pathology metadata
                    info = disease_info.get(pred_class, {
                        'crop': pred_class.split('___')[0],
                        'disease': pred_class.split('___')[1].replace('_', ' '),
                        'pathogen': 'Fungal / Microbial',
                        'severity': 'Moderate',
                        'symptoms': 'Foliar discoloration and necrotic lesions detected.',
                        'causes': 'Elevated humidity and microclimatic spore dispersal.',
                        'organic_control': ['Apply 5% Neem seed kernel extract', 'Spray bio-fungicide Trichoderma'],
                        'chemical_control': ['Mancozeb 75% WP @ 2.5 g/L water'],
                        'prevention': ['Ensure proper spacing and crop rotation']
                    })

                    result = {
                        'disease_key': pred_class,
                        'confidence': confidence,
                        'info': info
                    }

                    # Log to database
                    database.log_disease_scan(
                        os.path.basename(target_filepath),
                        info['crop'],
                        info['disease'],
                        confidence,
                        info['severity'],
                        info['organic_control'][0] if info['organic_control'] else 'None'
                    )
                    flash(f"Diagnosis completed: {info['crop']} - {info['disease']}", "success")
                else:
                    flash("Disease CNN model not available.", "error")
            else:
                flash("Please upload a leaf photo or pick a sample leaf.", "error")
        except Exception as e:
            flash(f"Error during disease scan: {str(e)}", "error")

    return render_template('disease.html', result=result, uploaded_image=uploaded_image_url)

@app.route('/fertilizer', methods=['GET', 'POST'])
def fertilizer_recommend():
    rec = None
    form_data = None
    if request.method == 'POST':
        try:
            soil_type = request.form.get('soil_type', 'Loamy')
            crop_type = request.form.get('crop_type', 'Paddy')
            n = float(request.form.get('nitrogen', 12))
            p = float(request.form.get('phosphorus', 28))
            k = float(request.form.get('potassium', 32))
            moist = float(request.form.get('moisture', 55))
            temp = 28.0
            hum = 65.0

            form_data = {
                'soil_type': soil_type, 'crop_type': crop_type,
                'nitrogen': n, 'phosphorus': p, 'potassium': k, 'moisture': moist
            }

            if fert_model and le_soil and le_crop and le_fert:
                # Safe encoding with fallback
                soil_code = le_soil.transform([soil_type])[0] if soil_type in le_soil.classes_ else 0
                crop_code = le_crop.transform([crop_type])[0] if crop_type in le_crop.classes_ else 0

                feat = np.array([[temp, hum, moist, soil_code, crop_code, n, k, p]])
                fert_idx = fert_model.predict(feat)[0]
                fert_name = le_fert.inverse_transform([fert_idx])[0]

                # Dosage calculation per acre and hectare
                dosage_map = {
                    'Urea': ('45 kg (1 Bag)', '110 kg'),
                    'DAP': ('50 kg (1 Bag)', '125 kg'),
                    '10-26-26': ('50 kg', '120 kg'),
                    '14-35-14': ('40 kg', '100 kg'),
                    '17-17-17': ('45 kg', '110 kg'),
                    '20-20': ('40 kg', '95 kg'),
                    '28-28-0': ('35 kg', '85 kg')
                }
                dosage_acre, dosage_ha = dosage_map.get(fert_name, ('45 kg', '110 kg'))

                rec = {
                    'fertilizer': fert_name,
                    'dosage_acre': dosage_acre,
                    'dosage_ha': dosage_ha
                }

                database.log_fertilizer_rec(crop_type, soil_type, n, p, k, fert_name, dosage_acre)
                flash(f"Fertilizer plan generated: {fert_name} recommended.", "success")
            else:
                flash("Fertilizer model not loaded.", "error")
        except Exception as e:
            flash(f"Error calculating fertilizer recommendation: {str(e)}", "error")

    return render_template('fertilizer.html', rec=rec, form_data=form_data)

@app.route('/weather', methods=['GET', 'POST'])
def weather_irrigation():
    city = request.args.get('city', 'Karnal') if request.method == 'GET' else request.form.get('city', 'Karnal')
    weather_data = get_agro_weather(city)
    irrig_rec = None

    if request.method == 'POST':
        try:
            crop = request.form.get('crop', 'Wheat')
            stage = request.form.get('stage', 'Vegetative')
            moisture = float(request.form.get('moisture', 38))
            area = float(request.form.get('area', 2.0))

            # Crop water coefficient multiplier
            crop_kc = {'Wheat': 1.0, 'Paddy': 1.6, 'Maize': 1.15, 'Cotton': 0.95, 'Sugarcane': 1.4, 'Vegetables': 1.05}.get(crop, 1.0)
            stage_factor = {'Vegetative': 0.9, 'Flowering': 1.25, 'Grain Filling': 1.1, 'Ripening': 0.4}.get(stage, 1.0)

            # Target moisture is 70%
            deficit = max(0, 70 - moisture)
            
            # Forecast rain in next 48 hours
            rain_48h = weather_data['forecast'][1]['rain'] + weather_data['forecast'][2]['rain']
            
            # Liters per acre calculation: 1 acre-mm = 4,046 Liters
            raw_depth_mm = (deficit * 0.5) * crop_kc * stage_factor
            effective_depth_mm = max(0, raw_depth_mm - (rain_48h * 0.6))
            total_liters = effective_depth_mm * 4046.86 * area

            if moisture < 35 and stage in ['Flowering', 'Grain Filling']:
                urgency = 'Critical'
                status = f'Critical Moisture Deficit — Irrigate Immediately ({crop} in {stage})'
                timing = 'Tomorrow Morning (6:00 AM - 9:00 AM)'
            elif moisture < 50 and rain_48h < 5:
                urgency = 'Moderate'
                status = 'Scheduled Irrigation Recommended within 24-36 Hours'
                timing = 'Early Morning (6:30 AM) or Late Afternoon (5:00 PM)'
            elif rain_48h > 10:
                urgency = 'Adequate'
                status = f'Sufficient Rain Forecasted ({rain_48h} mm) — Delay Irrigation'
                timing = 'Post-Rainfall Re-evaluation'
                total_liters = 0
            else:
                urgency = 'Adequate'
                status = 'Soil Moisture Adequate — No Irrigation Required'
                timing = 'Maintain Monitoring'
                total_liters = 0

            irrig_rec = {
                'crop': crop,
                'stage': stage,
                'moisture': moisture,
                'area': area,
                'water_liters': total_liters,
                'urgency': urgency,
                'status': status,
                'timing': timing
            }

            database.log_irrigation(crop, moisture, weather_data['current']['temp'], rain_48h, status, total_liters)
            flash(f"Smart irrigation calculation complete for {area} acres of {crop}.", "success")
        except Exception as e:
            flash(f"Error computing irrigation: {str(e)}", "error")

    return render_template('weather.html', weather=weather_data, city=city, irrig=irrig_rec)

@app.route('/chatbot')
def chatbot_ui():
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    try:
        data = request.get_json() or {}
        user_message = data.get('message', '').strip().lower()
        if not user_message:
            return jsonify({'response': 'Please enter a valid farming or agricultural query.'})

        # Match against intents
        matched_response = None
        matched_intent = 'general'
        max_matches = 0

        if chatbot_kb and 'intents' in chatbot_kb:
            for intent in chatbot_kb['intents']:
                matches = sum(1 for pattern in intent['patterns'] if pattern in user_message)
                if matches > max_matches:
                    max_matches = matches
                    matched_intent = intent['tag']
                    matched_response = np.random.choice(intent['responses'])

        if not matched_response:
            matched_response = (
                "That's a very important agricultural inquiry! For specific crop selection or fertilizer dosage, "
                "please use our specialized Crop Suitability and Fertilizer Calculation tabs. "
                "You can also ask me about PM-KISAN, Early Blight remedies, drip irrigation, or organic Jeevamrutha preparation."
            )

        # Log conversation
        database.log_chat(data.get('message', ''), matched_response, matched_intent)

        return jsonify({
            'response': matched_response,
            'intent': matched_intent
        })
    except Exception as e:
        return jsonify({'response': f"Advisory error: {str(e)}", 'intent': 'error'}), 500

@app.route('/analytics')
def analytics_view():
    return render_template('analytics.html')

# --- Multilingual Voice Assistant Routes ---

@app.route('/voice')
def voice_assistant():
    return render_template('voice.html')

@app.route('/api/voice/process', methods=['POST'])
def api_voice_process():
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        lang = data.get('language', 'hi').lower()

        if not query:
            return jsonify({'response': 'Please speak or provide a query.', 'intent': 'empty', 'language': lang})

        kb_entries = voice_kb.get('knowledge_base', {}).get(lang)
        if not kb_entries:
            # Fallback to English or Hindi if language not directly mapped
            kb_entries = voice_kb.get('knowledge_base', {}).get('en', [])

        matched_response = None
        matched_intent = 'general'
        max_score = 0

        query_lower = query.lower()
        for item in kb_entries:
            score = 0
            for kw in item.get('keywords', []):
                if kw.lower() in query_lower:
                    score += 1
            if score > max_score:
                max_score = score
                matched_intent = item.get('intent', 'general')
                matched_response = item.get('response')

        if not matched_response:
            # Localized fallback responses
            fallback_map = {
                'hi': "यह एक महत्वपूर्ण कृषि प्रश्न है। आप फसल चयन, पत्तों के रोग, खाद की मात्रा या सिंचाई के बारे में पूछ सकते हैं।",
                'mr': "हा एक महत्त्वाचा शेतीविषयक प्रश्न आहे. आपण पीक निवड, खतांचे प्रमाण किंवा सिंचनाबद्दल विचारू शकता.",
                'te': "ఇది ముఖ్యమైన వ్యవసాయ ప్రశ్న. మీరు పంటలు, ఎరువులు లేదా చీడపీడల గురించి అడగవచ్చు.",
                'ta': "இது ஒரு முக்கியமான விவசாய கேள்வி. பயிர் தேர்வு, உரம் அல்லது பூச்சி மேலாண்மை பற்றி கேளுங்கள்.",
                'bn': "এটি একটি গুরুত্বপূর্ণ কৃষি প্রশ্ন। আপনি ফসল নির্বাচন বা সার প্রয়োগ সম্পর্কে জিজ্ঞাসা করতে পারেন।",
                'gu': "આ એક મહત્વનો કૃષિ પ્રશ્ન છે. તમે પાકની પસંદગી કે ખાતર વિશે પૂછી શકો છો.",
                'kn': "ಇದು ಮುಖ್ಯವಾದ ಕೃಷಿ ಪ್ರಶ್ನೆ. ಬೆಳೆ ಆಯ್ಕೆ ಅಥವಾ ಗೊಬ್ಬರದ ಬಗ್ಗೆ ಕೇಳಿ.",
                'pa': "ਇਹ ਇੱਕ ਅਹਿਮ ਖੇਤੀ ਸਵਾਲ ਹੈ। ਤੁਸੀਂ ਫਸਲ ਜਾਂ ਖਾਦ ਬਾਰੇ ਪੁੱਛ ਸਕਦੇ ਹੋ।",
                'en': "That is an important farming inquiry. You can ask about crop suitability, fertilizer dosage, leaf blight remedies, or irrigation scheduling."
            }
            matched_response = fallback_map.get(lang, fallback_map['en'])

        # Log to SQLite voice_logs table
        database.log_voice(lang, query, matched_response, matched_intent)

        return jsonify({
            'query': query,
            'response': matched_response,
            'intent': matched_intent,
            'language': lang,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'response': f"Voice processing error: {str(e)}", 'status': 'error'}), 500

@app.route('/api/voice/tts')
def api_voice_tts():
    try:
        text = request.args.get('text', '').strip()
        lang = request.args.get('lang', 'hi').lower()
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Language code normalization for gTTS
        gtts_lang = lang if lang in ['hi', 'en', 'mr', 'ta', 'te', 'bn', 'gu', 'kn', 'pa'] else 'hi'

        # Create cache key
        cache_key = hashlib.md5(f"{text}_{gtts_lang}".encode('utf-8')).hexdigest()
        audio_filename = f"{cache_key}.mp3"
        audio_filepath = os.path.join(app.config['AUDIO_CACHE_FOLDER'], audio_filename)

        if not os.path.exists(audio_filepath):
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang=gtts_lang, slow=False)
                tts.save(audio_filepath)
            except Exception as tts_err:
                print(f"Warning: gTTS generation failed ({tts_err}), generating dummy tone or fallback.")
                return jsonify({'error': 'TTS synthesis unavailable'}), 503

        return send_file(audio_filepath, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/voice/languages')
def api_voice_languages():
    return jsonify(voice_kb.get('languages', {}))

# --- JSON REST APIs ---

@app.route('/api/predict/crop', methods=['POST'])
def api_predict_crop():
    try:
        data = request.get_json()
        n = float(data['nitrogen'])
        p = float(data['phosphorus'])
        k = float(data['potassium'])
        ph = float(data['ph'])
        temp = float(data['temperature'])
        hum = float(data['humidity'])
        rain = float(data['rainfall'])

        feat = np.array([[n, p, k, temp, hum, ph, rain]])
        probs = crop_model.predict_proba(feat)[0]
        best_idx = np.argmax(probs)
        best_crop = crop_model.classes_[best_idx]
        confidence = float(probs[best_idx])

        return jsonify({
            'recommended_crop': best_crop,
            'confidence': confidence,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'failed'}), 400

@app.route('/api/predict/fertilizer', methods=['POST'])
def api_predict_fertilizer():
    try:
        data = request.get_json()
        soil_type = data.get('soil_type', 'Loamy')
        crop_type = data.get('crop_type', 'Paddy')
        n = float(data['nitrogen'])
        p = float(data['phosphorus'])
        k = float(data['potassium'])
        moist = float(data.get('moisture', 50))
        temp = float(data.get('temperature', 28))
        hum = float(data.get('humidity', 65))

        soil_code = le_soil.transform([soil_type])[0]
        crop_code = le_crop.transform([crop_type])[0]
        feat = np.array([[temp, hum, moist, soil_code, crop_code, n, k, p]])

        fert_idx = fert_model.predict(feat)[0]
        fert_name = le_fert.inverse_transform([fert_idx])[0]

        return jsonify({
            'recommended_fertilizer': fert_name,
            'crop_type': crop_type,
            'soil_type': soil_type,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'failed'}), 400

if __name__ == '__main__':
    print("Starting AgriPulse AI Server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
