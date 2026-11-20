import os
import json
import tempfile
import numpy as np
import matplotlib
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFilter

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

with open('data/disease_info.json', 'r') as f:
    disease_info = json.load(f)

classes = sorted(list(disease_info.keys()))
num_classes = len(classes)

# Load the leaf generation function
def generate_leaf_pattern(cls_name, size=(128, 128)):
    img = Image.new('RGB', size, (230, 240, 230))
    draw = ImageDraw.Draw(img)
    
    # Distinctive crop leaf shapes & colors
    if 'corn' in cls_name.lower():
        leaf_color = (45, 150, 45) if 'healthy' in cls_name.lower() else (110, 130, 30)
        draw.polygon([(64, 5), (85, 40), (80, 95), (64, 125), (48, 95), (43, 40)], fill=leaf_color)
        draw.line([(64, 5), (64, 125)], fill=(30, 110, 30), width=3)
    elif 'apple' in cls_name.lower():
        leaf_color = (35, 135, 35) if 'healthy' in cls_name.lower() else (70, 100, 35)
        draw.ellipse([30, 15, 98, 115], fill=leaf_color)
        draw.line([(64, 15), (64, 115)], fill=(25, 90, 25), width=2)
    else: # Potato & Tomato
        leaf_color = (40, 140, 45) if 'healthy' in cls_name.lower() else (65, 110, 35)
        draw.polygon([(64, 10), (105, 50), (100, 100), (64, 120), (28, 100), (23, 50)], fill=leaf_color)
        draw.line([(64, 15), (64, 118)], fill=(30, 95, 30), width=2)

    # Specific symptom signatures
    if 'early_blight' in cls_name.lower():
        for off in [(48, 52), (75, 78)]:
            draw.ellipse([off[0]-14, off[1]-14, off[0]+14, off[1]+14], fill=(185, 165, 45))
            draw.ellipse([off[0]-9, off[1]-9, off[0]+9, off[1]+9], fill=(80, 40, 15))
            draw.ellipse([off[0]-4, off[1]-4, off[0]+4, off[1]+4], fill=(40, 20, 10))
    elif 'late_blight' in cls_name.lower():
        draw.polygon([(40, 35), (75, 40), (85, 70), (50, 65)], fill=(30, 35, 20))
        draw.polygon([(35, 80), (70, 75), (60, 105), (30, 95)], fill=(25, 30, 15))
    elif 'bacterial_spot' in cls_name.lower():
        for pt in [(48, 40), (55, 60), (75, 50), (45, 78), (80, 85), (60, 95), (68, 35)]:
            draw.ellipse([pt[0]-3, pt[1]-3, pt[0]+3, pt[1]+3], fill=(20, 15, 10))
    elif 'common_rust' in cls_name.lower():
        for pt in [(58, 35), (68, 55), (55, 75), (72, 85), (60, 105)]:
            draw.ellipse([pt[0]-5, pt[1]-5, pt[0]+5, pt[1]+5], fill=(200, 75, 15))
    elif 'northern_leaf_blight' in cls_name.lower():
        draw.ellipse([54, 40, 74, 90], fill=(120, 110, 80))
    elif 'apple_scab' in cls_name.lower():
        draw.ellipse([45, 40, 75, 65], fill=(45, 55, 30))
        draw.ellipse([60, 70, 85, 95], fill=(35, 45, 25))
    elif 'black_rot' in cls_name.lower():
        draw.ellipse([42, 52, 70, 80], fill=(95, 35, 55))
        draw.ellipse([48, 58, 64, 74], fill=(160, 140, 100))
    elif 'yellow_leaf_curl' in cls_name.lower():
        draw.polygon([(23, 50), (64, 10), (105, 50)], fill=(225, 215, 35))
        
    return img

print("Generating stratified synthetic training data...")
X_data = []
y_data = []

np.random.seed(42)
for idx, cls_name in enumerate(classes):
    for sample_i in range(50):
        base_img = generate_leaf_pattern(cls_name)
        # Random rotation & subtle jitter
        rot = base_img.rotate(np.random.uniform(-10, 10), resample=Image.BILINEAR, fillcolor=(230, 240, 230))
        arr = np.array(rot, dtype=np.float32) / 255.0
        # Add slight color variation
        noise = np.random.normal(0, 0.015, arr.shape)
        arr = np.clip(arr + noise, 0.0, 1.0)
        X_data.append(arr)
        y_data.append(idx)

X_data = np.array(X_data, dtype=np.float32)
y_data = np.array(y_data, dtype=np.int32)

X_train, X_test, y_train, y_test = train_test_split(
    X_data, y_data, test_size=0.2, random_state=42, stratify=y_data
)

y_train_cat = to_categorical(y_train, num_classes=num_classes)
y_test_cat = to_categorical(y_test, num_classes=num_classes)

print(f"X_train shape: {X_train.shape}, X_test shape: {X_test.shape}")

# High performance CNN Architecture with Softmax
model = models.Sequential([
    layers.Input(shape=(128, 128, 3)),
    layers.Conv2D(32, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),

    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),

    layers.Flatten(),
    layers.Dense(96, activation='relu'),
    layers.Dropout(0.25),
    layers.Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history = model.fit(
    X_train, y_train_cat,
    validation_data=(X_test, y_test_cat),
    epochs=12,
    batch_size=32,
    verbose=1
)

loss, acc = model.evaluate(X_test, y_test_cat, verbose=0)
print(f"TensorFlow CNN Final Test Accuracy: {acc * 100:.2f}%")

model.save('models/plant_disease_model.keras')

# Plot accurate training metrics
plt.figure(figsize=(9, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Acc', color='#2d7a4c', lw=2)
plt.plot(history.history['val_accuracy'], label='Val Acc', color='#52b788', linestyle='--', lw=2)
plt.title('CNN Disease Model Accuracy', fontsize=11, fontweight='bold')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss', color='#b02a37', lw=2)
plt.plot(history.history['val_loss'], label='Val Loss', color='#e07a5f', linestyle='--', lw=2)
plt.title('CNN Disease Model Loss Progression', fontsize=11, fontweight='bold')
plt.xlabel('Epoch')
plt.ylabel('Categorical Crossentropy Loss')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('static/img/disease_training_metrics.png', dpi=300)
plt.close()
print("Saved models/plant_disease_model.keras and static/img/disease_training_metrics.png")
