#!/usr/bin/env python3
"""
Швидкий тест IoT пристрою без запуску сервера
Використовує httpbin.org для тестування HTTP запитів
"""

import json
import time
import uuid
from datetime import datetime
import requests
from requests.exceptions import RequestException

def generate_test_data(device_id: str) -> dict:
    """Генерує тестові дані"""
    import random
    
    temperature = round(random.uniform(20.0, 30.0), 2)
    return {
        "device_id": device_id,
        "temperature": temperature,
        "unit": "celsius",
        "timestamp": datetime.now().isoformat(),
        "test_mode": True
    }

def test_http_request(data: dict, url: str = "https://httpbin.org/post") -> bool:
    """Тестує HTTP запит"""
    try:
        response = requests.post(
            url,
            json=data,
            timeout=10,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'IoT-Device-Test/1.0'
            }
        )
        
        response.raise_for_status()
        
        # Перевірка відповіді
        if url == "https://httpbin.org/post":
            response_data = response.json()
            sent_data = response_data.get('json', {})
            
            # Порівняння відправлених та отриманих даних
            if sent_data.get('device_id') == data.get('device_id'):
                print(f"✅ Тест пройдено: {data['temperature']}°C")
                return True
            else:
                print(f"❌ Помилка: дані не співпадають")
                return False
        else:
            print(f"✅ Запит успішний: {response.status_code}")
            return True
            
    except RequestException as e:
        print(f"❌ Помилка запиту: {e}")
        return False
    except Exception as e:
        print(f"❌ Неочікувана помилка: {e}")
        return False

def run_quick_test():
    """Запускає швидкий тест"""
    print("🚀 Запуск швидкого тесту IoT пристрою")
    print("📡 Використовується httpbin.org для тестування")
    print("-" * 50)
    
    device_id = str(uuid.uuid4())
    print(f"🆔 Device ID: {device_id}")
    
    # URLs для тестування
    test_urls = [
        "https://httpbin.org/post",
        "https://httpbin.org/status/200",
        "https://postman-echo.com/post"
    ]
    
    success_count = 0
    total_tests = 3
    
    for i in range(total_tests):
        print(f"\n📤 Тест {i + 1}/{total_tests}")
        
        # Генерація даних
        data = generate_test_data(device_id)
        
        # Тестування основного URL
        if test_http_request(data):
            success_count += 1
        
        # Затримка між тестами
        if i < total_tests - 1:
            print("⏳ Очікування 3 секунди...")
            time.sleep(3)
    
    # Результати
    print("\n" + "=" * 50)
    print(f"📊 Результати тестування:")
    print(f"   Успішно: {success_count}/{total_tests}")
    print(f"   Успішність: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 Всі тести пройдені успішно!")
    else:
        print("⚠️ Деякі тести не пройшли")
    
    # Додатковий тест різних URLs
    print("\n🔄 Додатковий тест різних endpoints:")
    for url in test_urls[1:]:
        print(f"   Тестування {url}...")
        test_data = generate_test_data(device_id)
        test_http_request(test_data, url)

def test_json_serialization():
    """Тестує серіалізацію JSON"""
    print("\n🧪 Тест серіалізації JSON:")
    
    test_data = {
        "device_id": str(uuid.uuid4()),
        "temperature": 25.67,
        "unit": "celsius",
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "location": "test_room",
            "sensor_type": "DHT22"
        }
    }
    
    try:
        json_str = json.dumps(test_data, indent=2)
        parsed_data = json.loads(json_str)
        
        print("✅ JSON серіалізація/десеріалізація успішна")
        print(f"   Розмір JSON: {len(json_str)} байт")
        
        return True
    except Exception as e:
        print(f"❌ Помилка JSON: {e}")
        return False

def main():
    """Головна функція тесту"""
    try:
        # Основний тест
        run_quick_test()
        
        # Тест JSON
        test_json_serialization()
        
        print("\n✨ Тестування завершено")
        
    except KeyboardInterrupt:
        print("\n🛑 Тестування перервано користувачем")
    except Exception as e:
        print(f"\n💥 Критична помилка: {e}")

if __name__ == "__main__":
    main()