import requests
import json
import random
import time
import uuid
from datetime import datetime

class IoTDevice:
    def __init__(self, webhook_url, device_id=None):
        """
        Ініціалізація IoT пристрою
        
        Args:
            webhook_url (str): URL для відправки даних
            device_id (str): Унікальний ідентифікатор пристрою (генерується автоматично, якщо не вказано)
        """
        self.webhook_url = webhook_url
        self.device_id = device_id or str(uuid.uuid4())
        self.min_temp = 20
        self.max_temp = 30
        
    def generate_temperature(self):
        """Генерує випадкову температуру від 20 до 30°C"""
        return round(random.uniform(self.min_temp, self.max_temp), 2)
    
    def create_payload(self, temperature):
        """Створює JSON payload з даними пристрою"""
        return {
            "device_id": self.device_id,
            "temperature": temperature,
            "unit": "celsius",
            "timestamp": datetime.now().isoformat()
        }
    
    def send_data(self, payload):
        """Відправляє дані на webhook URL"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': f'IoT-Device/{self.device_id}'
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Дані успішно відправлено: {payload['temperature']}°C")
            else:
                print(f"⚠️  Помилка відправки: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Помилка мережі: {e}")
        except Exception as e:
            print(f"❌ Неочікувана помилка: {e}")
    
    def run(self):
        """Запускає нескінченний цикл роботи пристрою"""
        print(f"🚀 IoT пристрій {self.device_id} запущено")
        print(f"📡 Відправка даних на: {self.webhook_url}")
        print("⏱️  Інтервал: 5 секунд")
        print("-" * 50)
        
        while True:
            try:
                # Генеруємо температуру
                temperature = self.generate_temperature()
                
                # Створюємо payload
                payload = self.create_payload(temperature)
                
                # Відправляємо дані
                self.send_data(payload)
                
                # Чекаємо 5 секунд
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\n🛑 Пристрій зупинено користувачем")
                break
            except Exception as e:
                print(f"❌ Критична помилка: {e}")
                print("🔄 Перезапуск через 5 секунд...")
                time.sleep(5)


def main():
    """Головна функція програми"""
    # URL для відправки даних (замініть на свій)
    webhook_url = "https://webhook.site/your-unique-url"
    
    # Створюємо та запускаємо IoT пристрій
    device = IoTDevice(webhook_url)
    device.run()


if __name__ == "__main__":
    main() 