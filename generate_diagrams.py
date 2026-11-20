import os
import tempfile
import matplotlib
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('static/img/diagrams', exist_ok=True)

# 1. System Architecture Diagram
fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Layer 1: Client
rect_client = patches.FancyBboxPatch((5, 75), 90, 18, boxstyle="round,pad=1", ec="#1b4332", fc="#d8f3dc", lw=2)
ax.add_patch(rect_client)
ax.text(50, 88, "PRESENTATION LAYER (HTML5, Modern CSS, Responsive JavaScript, Chart.js)", ha='center', va='center', fontsize=11, fontweight='bold', color='#1b4332')
ui_modules = ["Farmer Dashboard", "Crop Recommender", "Leaf Disease Vision", "Fertilizer Planner", "Agro-Weather / Irrigation", "AI Chatbot"]
for i, m in enumerate(ui_modules):
    x_pos = 10 + i * 14
    box = patches.FancyBboxPatch((x_pos, 77), 12, 8, boxstyle="round,pad=0.5", ec="#2d7a4c", fc="#ffffff", lw=1.5)
    ax.add_patch(box)
    ax.text(x_pos + 6, 81, m, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#2d7a4c', wrap=True)

# Arrow 1
ax.annotate('', xy=(50, 68), xytext=(50, 75), arrowprops=dict(arrowstyle="<->", color="#1b4332", lw=2))
ax.text(52, 71.5, "HTTP / JSON REST APIs", fontsize=8.5, color="#1b4332", fontweight='bold')

# Layer 2: Application Core
rect_app = patches.FancyBboxPatch((5, 45), 90, 22, boxstyle="round,pad=1", ec="#1e40af", fc="#dbeafe", lw=2)
ax.add_patch(rect_app)
ax.text(50, 62, "APPLICATION & AGENT ORCHESTRATION LAYER (Python Flask, Werkzeug)", ha='center', va='center', fontsize=11, fontweight='bold', color='#1e40af')

app_components = ["Flask Routing Engine", "Crop Decision Agent", "Vision Screening Agent", "Smart Integration Agent", "Chatbot NLP Engine"]
for i, c in enumerate(app_components):
    x_pos = 9 + i * 17
    box = patches.FancyBboxPatch((x_pos, 48), 15, 10, boxstyle="round,pad=0.5", ec="#1d4ed8", fc="#ffffff", lw=1.5)
    ax.add_patch(box)
    ax.text(x_pos + 7.5, 53, c, ha='center', va='center', fontsize=8, fontweight='bold', color='#1e3a8a')

# Arrow 2
ax.annotate('', xy=(50, 36), xytext=(50, 45), arrowprops=dict(arrowstyle="<->", color="#1e40af", lw=2))

# Layer 3: ML Models & Persistence
rect_data = patches.FancyBboxPatch((5, 8), 90, 26, boxstyle="round,pad=1", ec="#b45309", fc="#fef3c7", lw=2)
ax.add_patch(rect_data)
ax.text(50, 29, "MACHINE LEARNING, DEEP LEARNING & DATA PERSISTENCE LAYER", ha='center', va='center', fontsize=11, fontweight='bold', color='#b45309')

data_components = [
    "Scikit-Learn\nRandom Forest\n(Crop 99.77%)",
    "TensorFlow CNN\nDeep Classifier\n(14 Disease Classes)",
    "Nutrient Deficit\nDecision Tree\n(Fertilizer 99%)",
    "SQLite3 DB\n(History, Logs,\nAudits)",
    "External APIs\n(Open-Meteo Weather\n& Mandi Prices)"
]
for i, d in enumerate(data_components):
    x_pos = 9 + i * 17
    box = patches.FancyBboxPatch((x_pos, 11), 15, 14, boxstyle="round,pad=0.5", ec="#d97706", fc="#ffffff", lw=1.5)
    ax.add_patch(box)
    ax.text(x_pos + 7.5, 18, d, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#92400e')

plt.title("AgriPulse AI - End-to-End System Architecture", fontsize=14, fontweight='bold', pad=15, color='#1b4332')
plt.tight_layout()
plt.savefig('static/img/diagrams/system_architecture.png', dpi=300)
plt.close()
print("Generated static/img/diagrams/system_architecture.png")

# 2. Data Flow Diagram (DFD Level 1)
fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Farmer
farmer = patches.Rectangle((5, 40), 16, 20, ec="#1b4332", fc="#d8f3dc", lw=2)
ax.add_patch(farmer)
ax.text(13, 50, "FARMER / FPO\nUSER", ha='center', va='center', fontweight='bold', fontsize=9, color='#1b4332')

# Processes
p1 = patches.Circle((40, 75), 10, ec="#2d7a4c", fc="#ffffff", lw=2)
p2 = patches.Circle((40, 25), 10, ec="#2d7a4c", fc="#ffffff", lw=2)
p3 = patches.Circle((75, 75), 10, ec="#2d7a4c", fc="#ffffff", lw=2)
p4 = patches.Circle((75, 25), 10, ec="#2d7a4c", fc="#ffffff", lw=2)
ax.add_patch(p1); ax.add_patch(p2); ax.add_patch(p3); ax.add_patch(p4)

ax.text(40, 75, "1.0\nCrop\nRecommendation", ha='center', va='center', fontsize=8, fontweight='bold', color='#1b4332')
ax.text(40, 25, "2.0\nLeaf Disease\nDiagnosis", ha='center', va='center', fontsize=8, fontweight='bold', color='#1b4332')
ax.text(75, 75, "3.0\nFertilizer\nOptimization", ha='center', va='center', fontsize=8, fontweight='bold', color='#1b4332')
ax.text(75, 25, "4.0\nSmart\nIrrigation", ha='center', va='center', fontsize=8, fontweight='bold', color='#1b4332')

# DB Store
db_box = patches.FancyBboxPatch((52, 45), 16, 12, boxstyle="round,pad=0.5", ec="#1e3a8a", fc="#dbeafe", lw=1.5)
ax.add_patch(db_box)
ax.text(60, 51, "D1: SQLite Database\n(Logs & Audits)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1e3a8a')

# Flow arrows
ax.annotate('Soil N-P-K, pH, Rain', xy=(30, 75), xytext=(21, 55), arrowprops=dict(arrowstyle="->", color="#1b4332", lw=1.5))
ax.annotate('Leaf Image', xy=(30, 25), xytext=(21, 45), arrowprops=dict(arrowstyle="->", color="#1b4332", lw=1.5))
ax.annotate('Rec. Crop', xy=(21, 58), xytext=(30, 80), arrowprops=dict(arrowstyle="->", color="#15803d", lw=1.5, ls='--'))
ax.annotate('Remedies', xy=(21, 42), xytext=(30, 20), arrowprops=dict(arrowstyle="->", color="#15803d", lw=1.5, ls='--'))

ax.annotate('', xy=(52, 53), xytext=(48, 70), arrowprops=dict(arrowstyle="->", color="#1e3a8a", lw=1))
ax.annotate('', xy=(52, 49), xytext=(48, 30), arrowprops=dict(arrowstyle="->", color="#1e3a8a", lw=1))

plt.title("AgriPulse AI - Data Flow Diagram (Level 1)", fontsize=13, fontweight='bold', pad=15, color='#1b4332')
plt.tight_layout()
plt.savefig('static/img/diagrams/data_flow_diagram.png', dpi=300)
plt.close()
print("Generated static/img/diagrams/data_flow_diagram.png")

# 3. Database ER Diagram
fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

tables = [
    ("crop_predictions", 10, 55, ["id (PK, Integer)", "timestamp (DateTime)", "nitrogen (Real)", "phosphorus (Real)", "potassium (Real)", "temperature (Real)", "humidity (Real)", "ph (Real)", "rainfall (Real)", "predicted_crop (Text)", "confidence (Real)"]),
    ("disease_scans", 55, 55, ["id (PK, Integer)", "timestamp (DateTime)", "filename (Text)", "crop (Text)", "disease (Text)", "confidence (Real)", "severity (Text)", "action_taken (Text)"]),
    ("fertilizer_recommendations", 10, 10, ["id (PK, Integer)", "timestamp (DateTime)", "crop_type (Text)", "soil_type (Text)", "n_val, p_val, k_val (Real)", "fertilizer (Text)", "dosage (Text)"]),
    ("irrigation_logs", 55, 10, ["id (PK, Integer)", "timestamp (DateTime)", "crop (Text)", "soil_moisture (Real)", "temperature (Real)", "rain_forecast (Real)", "status (Text)", "water_liters (Real)"])
]

for name, x, y, fields in tables:
    header = patches.Rectangle((x, y + len(fields)*3), 36, 4, ec="#1b4332", fc="#2d7a4c", lw=1.5)
    body = patches.Rectangle((x, y), 36, len(fields)*3, ec="#1b4332", fc="#f0fdf4", lw=1.5)
    ax.add_patch(body); ax.add_patch(header)
    ax.text(x + 18, y + len(fields)*3 + 2, f"TABLE: {name}", ha='center', va='center', color='white', fontweight='bold', fontsize=8.5)
    for i, f in enumerate(fields):
        ax.text(x + 2, y + len(fields)*3 - (i*3) - 1.8, f"• {f}", fontsize=7.5, color='#1f2937')

plt.title("AgriPulse AI - Relational Database Entity-Relationship (ER) Schema", fontsize=13, fontweight='bold', pad=15, color='#1b4332')
plt.tight_layout()
plt.savefig('static/img/diagrams/database_er_diagram.png', dpi=300)
plt.close()
print("Generated static/img/diagrams/database_er_diagram.png")
