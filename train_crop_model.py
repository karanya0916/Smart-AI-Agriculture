import os
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

os.makedirs('models', exist_ok=True)
os.makedirs('static/img', exist_ok=True)

# Load data
df = pd.read_csv('data/crop_recommendation.csv')
X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = df['label']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, output_dict=True)

print(f"Crop Recommendation Model Trained Successfully! Accuracy: {accuracy * 100:.2f}%")

# Save model
joblib.dump(model, 'models/crop_model.pkl')

# Save metrics
metrics = {
    'model_name': 'RandomForestClassifier (100 Estimators)',
    'accuracy': round(accuracy, 4),
    'samples_trained': len(X_train),
    'samples_tested': len(X_test),
    'classes': list(model.classes_),
    'feature_names': list(X.columns)
}
with open('models/crop_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=4)

# Feature Importance Plot
plt.figure(figsize=(8, 4.5))
plt.style.use('ggplot')
importances = model.feature_importances_
indices = np.argsort(importances)[::-1]
features = X.columns

plt.bar(range(X.shape[1]), importances[indices], color='#2d7a4c', align='center')
plt.xticks(range(X.shape[1]), [features[i] for i in indices], rotation=30)
plt.title('Crop Recommendation - Feature Importance Analysis', fontsize=12, fontweight='bold', color='#1b4332')
plt.ylabel('Relative Importance Score')
plt.tight_layout()
plt.savefig('static/img/crop_feature_importance.png', dpi=300)
plt.close()

# Save confusion matrix plot
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(10, 8))
plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Greens)
plt.title('Confusion Matrix - Crop Suitability Model (Test Set)', fontsize=12, fontweight='bold')
plt.colorbar()
tick_marks = np.arange(len(model.classes_))
plt.xticks(tick_marks, model.classes_, rotation=90, fontsize=8)
plt.yticks(tick_marks, model.classes_, fontsize=8)
plt.ylabel('True Crop Label')
plt.xlabel('Predicted Crop Label')
plt.tight_layout()
plt.savefig('static/img/crop_confusion_matrix.png', dpi=300)
plt.close()

print("Artifacts saved to models/ and static/img/")
