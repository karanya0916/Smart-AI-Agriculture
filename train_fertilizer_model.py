import os
import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

os.makedirs('models', exist_ok=True)

df = pd.read_csv('data/fertilizer_data.csv')

le_soil = LabelEncoder()
le_crop = LabelEncoder()
le_fert = LabelEncoder()

df['Soil_Type_Code'] = le_soil.fit_transform(df['Soil_Type'])
df['Crop_Type_Code'] = le_crop.fit_transform(df['Crop_Type'])
df['Fertilizer_Code'] = le_fert.fit_transform(df['Fertilizer_Name'])

feature_cols = ['Temparature', 'Humidity', 'Moisture', 'Soil_Type_Code', 'Crop_Type_Code', 'Nitrogen', 'Potassium', 'Phosphorous']
X = df[feature_cols]
y = df['Fertilizer_Code']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

acc = accuracy_score(y_test, clf.predict(X_test))
print(f"Fertilizer Model Trained Successfully! Test Accuracy: {acc * 100:.2f}%")

# Save model and encoders
joblib.dump(clf, 'models/fertilizer_model.pkl')
joblib.dump(le_soil, 'models/soil_encoder.pkl')
joblib.dump(le_crop, 'models/crop_fert_encoder.pkl')
joblib.dump(le_fert, 'models/fert_encoder.pkl')

fert_meta = {
    'accuracy': round(acc, 4),
    'soil_types': list(le_soil.classes_),
    'crop_types': list(le_crop.classes_),
    'fertilizers': list(le_fert.classes_),
    'features': feature_cols
}
with open('models/fertilizer_meta.json', 'w') as f:
    json.dump(fert_meta, f, indent=4)

print("Fertilizer model artifacts serialized to models/")
