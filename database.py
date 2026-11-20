import sqlite3
import os
from datetime import datetime

DB_PATH = 'data/agri_assistant.db'

def get_db_connection():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Crop Predictions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crop_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            nitrogen REAL,
            phosphorus REAL,
            potassium REAL,
            temperature REAL,
            humidity REAL,
            ph REAL,
            rainfall REAL,
            predicted_crop TEXT,
            confidence REAL
        )
    ''')
    
    # 2. Disease Scans Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS disease_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            filename TEXT,
            crop TEXT,
            disease TEXT,
            confidence REAL,
            severity TEXT,
            action_taken TEXT
        )
    ''')
    
    # 3. Fertilizer Recommendations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fertilizer_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            crop_type TEXT,
            soil_type TEXT,
            n_val REAL,
            p_val REAL,
            k_val REAL,
            fertilizer TEXT,
            dosage TEXT
        )
    ''')
    
    # 4. Smart Irrigation Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS irrigation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            crop TEXT,
            soil_moisture REAL,
            temperature REAL,
            rain_forecast REAL,
            status TEXT,
            water_liters REAL
        )
    ''')
    
    # 5. Chat History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_message TEXT,
            bot_reply TEXT,
            intent TEXT
        )
    ''')
    
    # 6. Voice Assistant Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            language TEXT,
            query_text TEXT,
            response_text TEXT,
            intent TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully at data/agri_assistant.db")

# Helper functions to log events
def log_crop_prediction(n, p, k, temp, hum, ph, rain, crop, conf):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO crop_predictions (nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, predicted_crop, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (n, p, k, temp, hum, ph, rain, crop, conf))
    conn.commit()
    conn.close()

def log_disease_scan(filename, crop, disease, conf, severity, action):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO disease_scans (filename, crop, disease, confidence, severity, action_taken)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (filename, crop, disease, conf, severity, action))
    conn.commit()
    conn.close()

def log_fertilizer_rec(crop, soil, n, p, k, fert, dosage):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO fertilizer_recommendations (crop_type, soil_type, n_val, p_val, k_val, fertilizer, dosage)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (crop, soil, n, p, k, fert, dosage))
    conn.commit()
    conn.close()

def log_irrigation(crop, moisture, temp, rain, status, liters):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO irrigation_logs (crop, soil_moisture, temperature, rain_forecast, status, water_liters)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (crop, moisture, temp, rain, status, liters))
    conn.commit()
    conn.close()

def log_chat(user_msg, bot_msg, intent):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO chat_history (user_message, bot_reply, intent)
        VALUES (?, ?, ?)
    ''', (user_msg, bot_msg, intent))
    conn.commit()
    conn.close()

def log_voice(language, query_text, response_text, intent):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO voice_logs (language, query_text, response_text, intent)
        VALUES (?, ?, ?, ?)
    ''', (language, query_text, response_text, intent))
    conn.commit()
    conn.close()

def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    crop_count = cursor.execute('SELECT COUNT(*) FROM crop_predictions').fetchone()[0]
    disease_count = cursor.execute('SELECT COUNT(*) FROM disease_scans').fetchone()[0]
    fert_count = cursor.execute('SELECT COUNT(*) FROM fertilizer_recommendations').fetchone()[0]
    irrig_count = cursor.execute('SELECT COUNT(*) FROM irrigation_logs').fetchone()[0]
    voice_count = cursor.execute('SELECT COUNT(*) FROM voice_logs').fetchone()[0]
    
    recent_crops = cursor.execute('SELECT * FROM crop_predictions ORDER BY timestamp DESC LIMIT 5').fetchall()
    recent_diseases = cursor.execute('SELECT * FROM disease_scans ORDER BY timestamp DESC LIMIT 5').fetchall()
    
    conn.close()
    return {
        'crop_count': crop_count,
        'disease_count': disease_count,
        'fert_count': fert_count,
        'irrig_count': irrig_count,
        'voice_count': voice_count,
        'recent_crops': [dict(row) for row in recent_crops],
        'recent_diseases': [dict(row) for row in recent_diseases]
    }

if __name__ == '__main__':
    init_db()
