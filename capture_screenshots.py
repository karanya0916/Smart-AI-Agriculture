import os
import time
import subprocess
import threading
from app import app

os.makedirs('static/screenshots', exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def run_server():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

# Start server in thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
print("Server thread started. Waiting 2 seconds for warm up...")
time.sleep(2)

pages = [
    ('dashboard', 'http://127.0.0.1:5000/', 'screenshot_01_dashboard.png'),
    ('crop', 'http://127.0.0.1:5000/crop', 'screenshot_02_crop.png'),
    ('disease', 'http://127.0.0.1:5000/disease', 'screenshot_03_disease.png'),
    ('fertilizer', 'http://127.0.0.1:5000/fertilizer', 'screenshot_04_fertilizer.png'),
    ('weather', 'http://127.0.0.1:5000/weather', 'screenshot_05_weather.png'),
    ('chatbot', 'http://127.0.0.1:5000/chatbot', 'screenshot_06_chatbot.png'),
    ('voice', 'http://127.0.0.1:5000/voice', 'screenshot_08_voice.png'),
    ('analytics', 'http://127.0.0.1:5000/analytics', 'screenshot_07_analytics.png')
]

for name, url, filename in pages:
    out_path = os.path.abspath(os.path.join('static', 'screenshots', filename))
    cmd = [
        CHROME_PATH,
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--hide-scrollbars',
        '--window-size=1280,820',
        f'--screenshot={out_path}',
        url
    ]
    print(f"Capturing screenshot for {name} from {url}...")
    try:
        subprocess.run(cmd, timeout=15, check=True)
        print(f"Saved: {out_path} (Size: {os.path.getsize(out_path)} bytes)")
    except Exception as e:
        print(f"Error capturing {name}: {e}")

print("Screenshot capture completed!")
