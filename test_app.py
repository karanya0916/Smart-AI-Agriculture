import os
import unittest
import json
from app import app
import database

class AgriPulseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_01_dashboard(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Farmer Decision Dashboard', response.data)
        print("✓ Test Dashboard: Passed")

    def test_02_crop_recommendation(self):
        data = {
            'nitrogen': '80',
            'phosphorus': '48',
            'potassium': '40',
            'ph': '6.5',
            'temperature': '24.5',
            'humidity': '80',
            'rainfall': '210'
        }
        response = self.client.post('/crop', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Recommended Crop', response.data)
        self.assertIn(b'rice', response.data.lower())
        print("✓ Test Crop Recommendation (Rice): Passed")

    def test_03_disease_detection_sample(self):
        data = {
            'sample_path': 'static/img/sample_leaves/potato_early_blight.jpg'
        }
        response = self.client.post('/disease', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Pathology Report', response.data)
        self.assertIn(b'Potato', response.data)
        print("✓ Test Leaf Disease Vision (Potato Early Blight): Passed")

    def test_04_fertilizer_recommendation(self):
        data = {
            'soil_type': 'Loamy',
            'crop_type': 'Paddy',
            'nitrogen': '10',
            'phosphorus': '30',
            'potassium': '35',
            'moisture': '60'
        }
        response = self.client.post('/fertilizer', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Recommended Fertilizer Formulation', response.data)
        print("✓ Test Fertilizer Recommendation: Passed")

    def test_05_weather_and_irrigation(self):
        data = {
            'city': 'Karnal',
            'crop': 'Wheat',
            'stage': 'Flowering',
            'moisture': '28',
            'area': '3.0'
        }
        response = self.client.post('/weather', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Water Scheduling Recommendation', response.data)
        print("✓ Test Weather & Smart Irrigation: Passed")

    def test_06_chatbot_api(self):
        payload = json.dumps({'message': 'how to treat early blight on potato?'})
        response = self.client.post('/api/chat', data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        res_data = json.loads(response.data)
        self.assertIn('response', res_data)
        print(f"✓ Test Chatbot API: Passed (Response: {res_data['response'][:60]}...)")

    def test_07_analytics_page(self):
        response = self.client.get('/analytics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Model Cards', response.data)
        print("✓ Test Analytics & Model Cards: Passed")

    def test_08_voice_assistant_page(self):
        response = self.client.get('/voice')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Multilingual Voice Assistant', response.data)
        print("✓ Test Voice Assistant Page: Passed")

    def test_09_voice_process_hindi(self):
        payload = json.dumps({'query': 'यूरिया खाद कितनी मात्रा में डालें?', 'language': 'hi'})
        response = self.client.post('/api/voice/process', data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertEqual(data['intent'], 'fertilizer_urea')
        print(f"✓ Test Multilingual Voice API (Hindi): Passed (Intent: {data['intent']})")

    def test_10_voice_process_marathi(self):
        payload = json.dumps({'query': 'पानांवरील करपा रोगाचे उपाय सांगा', 'language': 'mr'})
        response = self.client.post('/api/voice/process', data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertEqual(data['intent'], 'disease_blight')
        print(f"✓ Test Multilingual Voice API (Marathi): Passed (Intent: {data['intent']})")

    def test_11_voice_languages(self):
        response = self.client.get('/api/voice/languages')
        self.assertEqual(response.status_code, 200)
        langs = json.loads(response.data)
        self.assertIn('hi', langs)
        self.assertIn('te', langs)
        self.assertIn('mr', langs)
        print(f"✓ Test Voice Languages Endpoint: Passed ({len(langs)} regional languages loaded)")

if __name__ == '__main__':
    unittest.main()
