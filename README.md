# AgriPulse AI: AI-Based Smart Agriculture Assistant

[![Python 3.12](https://img.shields.io/badge/Python-3.12-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask%203.1-emerald.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![TensorFlow](https://img.shields.io/badge/Deep%20Learning-TensorFlow%20Keras-red.svg)](https://www.tensorflow.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-blue.svg)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade, data-driven agricultural decision-support web application designed to bridge the digital divide for smallholder farmers, Farmer Producer Organisations (FPOs), and agricultural extension officers.

---

## 🌟 Key Modules & Features

1. **🌾 Crop Recommendation Engine**
   - Inputs: Soil Nitrogen ($N$), Phosphorus ($P$), Potassium ($K$), Soil $pH$, Temperature ($^\circ C$), Humidity ($\%$), Rainfall ($mm$).
   - Algorithm: Random Forest Classifier (100 Estimators) trained on 22 agricultural crop varieties.
   - Accuracy: **99.77%** on held-out test data.

2. **🔬 Plant Leaf Disease Vision Diagnostic**
   - Inputs: Leaf photograph upload (JPG/PNG) or 1-Click pre-validated reference samples.
   - Deep Learning Engine: TensorFlow Sequential Convolutional Neural Network (CNN) with Batch Normalization & Dropout.
   - Capabilities: Identifies 14 foliar disease conditions across Potato, Tomato, Corn, and Apple with calibrated confidence, pathogen identification, symptoms, biological remedies, and chemical treatment guidelines.

3. **🧪 Fertilizer Recommendation Engine**
   - Inputs: Soil texture, target crop, and existing N-P-K reserves.
   - Algorithm: Decision Tree / Forest Nutrient Balancing Engine (**99.00% accuracy**).
   - Outputs: Exact commercial fertilizer formulation (Urea, DAP, 10-26-26, 14-35-14, 17-17-17), dosage per acre & hectare, and a 3-stage application schedule (Basal, Active Tillering, Panicle/Flowering).

4. **🌦️ Agro-Weather Forecast & Smart Irrigation**
   - Features: Real-time temperature, humidity, wind, 5-day precipitation forecast.
   - Smart Irrigation Engine: Computes evapotranspiration and soil moisture deficit to calculate water volume required in liters/acre and optimal watering windows.

5. **💬 AI Agriculture Chatbot (Kisan Sahayak)**
   - Context-aware natural language assistant indexed on agricultural knowledge (pests, fertilizers, schemes like PM-KISAN & PMFBY, organic farming recipes).

6. **🎙️ Multilingual Voice Assistant Tool (Kisan Dhwani)**
   - Hands-free voice recognition and speech synthesis in 9 Indian regional languages: English, हिन्दी (Hindi), मराठी (Marathi), తెలుగు (Telugu), தமிழ் (Tamil), বাংলা (Bengali), ગુજરાતી (Gujarati), ಕನ್ನಡ (Kannada), and ਪੰਜਾਬੀ (Punjabi).
   - Real-time client-side Speech-to-Text (Web Speech API) with animated audio sound wave visualizer, server-side multilingual intent classification, dual-mode Text-to-Speech synthesis (browser SpeechSynthesis API paired with server-side gTTS audio fallback), and 1-click sample voice queries for fast testing.

7. **📊 Farmer Decision Dashboard & Commodity Analytics**
   - Responsive emerald agriculture UI, KPI stat counters, soil health radar chart, recent activity logs, and benchmark mandi commodity price trends with food security supply risk flags.

---

## 📁 Project Directory Structure

```
geetanjali new project/
├── data/
│   ├── crop_recommendation.csv        # Kaggle/ICAR 22-crop benchmark dataset
│   ├── fertilizer_data.csv            # Soil NPK deficit decision dataset
│   ├── disease_info.json              # Agronomic pathology metadata & remedies
│   ├── chatbot_kb.json                # Agriculture conversational knowledge base
│   └── agri_assistant.db              # SQLite relational audit database
├── models/
│   ├── crop_model.pkl                 # Serialized Random Forest crop model
│   ├── fertilizer_model.pkl           # Serialized fertilizer model & encoders
│   ├── plant_disease_model.keras      # Trained TensorFlow Keras CNN model
│   └── disease_classes.json           # 14 target foliar disease labels
├── static/
│   ├── css/style.css                  # Green agriculture theme & responsive grid
│   ├── js/main.js                     # Sliders sync, drag-drop upload, chatbot AJAX
│   ├── img/
│   │   ├── crop_feature_importance.png
│   │   ├── crop_confusion_matrix.png
│   │   ├── disease_training_metrics.png
│   │   ├── diagrams/                  # System architecture, DFD, and ER diagrams
│   │   └── sample_leaves/             # Pre-generated sample leaves for instant demo
│   └── screenshots/                   # Actual running web application screenshots
├── templates/
│   ├── base.html                      # Layout, navigation, and footer
│   ├── index.html                     # Farmer decision dashboard
│   ├── crop.html                      # Crop suitability recommender
│   ├── disease.html                   # Leaf disease vision diagnostics
│   ├── fertilizer.html                # Fertilizer optimization engine
│   ├── weather.html                   # Agro-weather & smart irrigation
│   ├── chatbot.html                   # Conversational AI assistant
│   └── analytics.html                 # Model cards & commodity trends
├── app.py                             # Main Flask web application & REST API
├── database.py                        # SQLite schema and transactional helpers
├── train_crop_model.py                # Model training script for crop recommender
├── train_fertilizer_model.py          # Model training script for fertilizer engine
├── train_disease_model.py             # Model training script for TensorFlow CNN
├── capture_screenshots.py             # Headless Chrome script to capture UI screens
├── generate_diagrams.py               # Generates architecture, DFD & ER PNG diagrams
├── generate_docs.py                   # Generates official DOCX and PDF dossiers
├── test_app.py                        # End-to-end automated unit test suite
├── requirements.txt                   # Project dependencies
├── AgriPulse_AI_Project_Documentation.docx # Comprehensive Hackathon DOCX Report (2.1 MB)
├── AgriPulse_AI_Project_Documentation.pdf  # Comprehensive Hackathon PDF Report (1.9 MB)
└── README.md                          # Project documentation and guide
```

---

## 🚀 Quick Setup & Installation

### 1. Clone or Open the Workspace
```bash
cd "geetanjali new project"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Models (Pre-Trained & Ready)
All models are pre-trained and serialized in `models/`. To retrain from scratch:
```powershell
python train_crop_model.py; python train_fertilizer_model.py; python train_disease_model.py
```

### 4. Run Automated Test Suite
```bash
python test_app.py
```
*Output: All 7 unit and integration tests passing (`OK`).*

### 5. Launch Application
```bash
python app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 📄 Complete Project Documentation Dossier

As required for hackathon submission, complete project reports have been generated:
- **DOCX Format:** [AgriPulse_AI_Project_Documentation.docx](file:///c:/Users/sargu_3niengw/OneDrive/Desktop/geetanjali%20new%20project/AgriPulse_AI_Project_Documentation.docx) (~2.1 MB)
- **PDF Format:** [AgriPulse_AI_Project_Documentation.pdf](file:///c:/Users/sargu_3niengw/OneDrive/Desktop/geetanjali%20new%20project/AgriPulse_AI_Project_Documentation.pdf) (~1.9 MB)

Both documents contain all 20 required sections, full architecture, DFD, ER diagrams, test metrics, and high-resolution screenshots of the actual running application.
