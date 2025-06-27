from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Зберігаємо останні дані
last_data = None

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint для прийому даних від IoT пристрою"""
    global last_data
    
    try:
        data = request.get_json()
        last_data = data
        
        print(f"📥 Отримано дані від IoT пристрою:")
        print(f"   Device ID: {data.get('device_id')}")
        print(f"   Temperature: {data.get('temperature')}°C")
        print(f"   Unit: {data.get('unit')}")
        print(f"   Timestamp: {data.get('timestamp')}")
        print("-" * 40)
        
        return jsonify({"status": "success", "message": "Data received"}), 200
        
    except Exception as e:
        print(f"❌ Помилка обробки даних: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/last-data', methods=['GET'])
def get_last_data():
    """Endpoint для перегляду останніх отриманих даних"""
    if last_data:
        return jsonify(last_data), 200
    else:
        return jsonify({"message": "No data received yet"}), 404

@app.route('/', methods=['GET'])
def home():
    """Головна сторінка з інструкціями"""
    return """
    <h1>IoT Device Test Server</h1>
    <p>Цей сервер приймає дані від IoT пристрою.</p>
    <ul>
        <li><strong>Webhook URL:</strong> <code>http://localhost:5000/webhook</code></li>
        <li><strong>Перегляд останніх даних:</strong> <a href="/last-data">/last-data</a></li>
    </ul>
    <p>Для тестування змініть URL в <code>iot_device.py</code> на:</p>
    <code>webhook_url = "http://localhost:5000/webhook"</code>
    """

if __name__ == '__main__':
    print("🚀 Запуск тестового сервера...")
    print("📡 Webhook URL: http://localhost:5000/webhook")
    print("🌐 Головна сторінка: http://localhost:5000")
    print("📊 Останні дані: http://localhost:5000/last-data")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True) 