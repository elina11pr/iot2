#!/usr/bin/env python3
"""
Швидкий тест IoT пристрою без зовнішнього сервера
"""

import requests
import json
import random
import time
import uuid
from datetime import datetime

def test_iot_device():
    """Тестує IoT пристрій з використанням httpbin.org"""
    
    device_id = str(uuid.uuid4())
    webhook_url = "https://httpbin.org/post"  # Безкоштовний сервіс для тестування
    
    print(f"🧪 Тестування IoT пристрою")
    print(f"🆔 Device ID: {device_id}")
    print(f"📡 URL: {webhook_url}")
    print(f"⏱️  Інтервал: 5 секунд")
    print(f"🔄 Кількість тестів: 3")
    print("-" * 50)
    
    for i in range(3):
        try:
            # Генеруємо температуру
            temperature = round(random.uniform(20, 30), 2)
            
            # Створюємо payload
            payload = {
                "device_id": device_id,
                "temperature": temperature,
                "unit": "celsius",
                "timestamp": datetime.now().isoformat()
            }
            
            # Відправляємо дані
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': f'IoT-Device/{device_id}'
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Тест {i+1}/3: Дані відправлено - {temperature}°C")
                print(f"   Response: {response.status_code}")
            else:
                print(f"⚠️  Тест {i+1}/3: Помилка - HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Тест {i+1}/3: Помилка мережі - {e}")
        except Exception as e:
            print(f"❌ Тест {i+1}/3: Неочікувана помилка - {e}")
        
        if i < 2:  # Не чекаємо після останнього тесту
            print("⏳ Чекаємо 5 секунд...")
            time.sleep(5)
    
    print("-" * 50)
    print("🎉 Тестування завершено!")

if __name__ == "__main__":
    test_iot_device() 