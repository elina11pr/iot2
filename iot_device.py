#!/usr/bin/env python3
"""
IoT пристрій симулятор з покращеною обробкою помилок
Генерує випадкові дані температури та відправляє через HTTP POST
"""

import json
import random
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import requests
from requests.exceptions import (
    ConnectionError, 
    Timeout, 
    HTTPError, 
    RequestException
)
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('iot_device.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IoTDevice:
    """Клас для симуляції IoT пристрою"""
    
    def __init__(self, device_id: Optional[str] = None, webhook_url: str = ""):
        """
        Ініціалізація IoT пристрою
        
        Args:
            device_id: Унікальний ідентифікатор пристрою
            webhook_url: URL для відправки даних
        """
        self.device_id = device_id or str(uuid.uuid4())
        self.webhook_url = webhook_url or "https://httpbin.org/post"
        self.min_temp = 20.0
        self.max_temp = 30.0
        self.interval = 5  # секунди
        self.max_retries = 3
        self.retry_delay = 2  # секунди
        self.request_timeout = 10  # секунди
        self.session = requests.Session()
        
        # Налаштування HTTP сесії
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'IoT-Device/{self.device_id}'
        })
        
        logger.info(f"IoT пристрій ініціалізовано: {self.device_id}")
        logger.info(f"Webhook URL: {self.webhook_url}")

    def generate_temperature_data(self) -> Dict[str, Any]:
        """
        Генерує дані температури
        
        Returns:
            Словник з даними пристрою
        """
        temperature = round(random.uniform(self.min_temp, self.max_temp), 2)
        timestamp = datetime.now().isoformat()
        
        data = {
            "device_id": self.device_id,
            "temperature": temperature,
            "unit": "celsius",
            "timestamp": timestamp,
            "metadata": {
                "sensor_type": "temperature",
                "location": "room_1",
                "status": "active"
            }
        }
        
        logger.debug(f"Згенеровано дані: {temperature}°C")
        return data

    def send_data(self, data: Dict[str, Any]) -> bool:
        """
        Відправляє дані на webhook з повторними спробами
        
        Args:
            data: Дані для відправки
            
        Returns:
            True якщо успішно відправлено, False - інакше
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    self.webhook_url,
                    json=data,
                    timeout=self.request_timeout
                )
                
                # Перевірка HTTP статусу
                response.raise_for_status()
                
                logger.info(f"✅ Дані успішно відправлено: {data['temperature']}°C")
                logger.debug(f"HTTP Status: {response.status_code}")
                return True
                
            except ConnectionError as e:
                logger.warning(f"❌ Помилка з'єднання (спроба {attempt}/{self.max_retries}): {e}")
                
            except Timeout as e:
                logger.warning(f"⏰ Тайм-аут (спроба {attempt}/{self.max_retries}): {e}")
                
            except HTTPError as e:
                logger.error(f"🚫 HTTP помилка: {e.response.status_code} - {e}")
                if e.response.status_code < 500:
                    # Клієнтська помилка (4xx) - не повторювати
                    return False
                    
            except RequestException as e:
                logger.error(f"📡 Помилка запиту (спроба {attempt}/{self.max_retries}): {e}")
                
            except Exception as e:
                logger.error(f"💥 Неочікувана помилка: {e}")
                
            # Затримка перед наступною спробою
            if attempt < self.max_retries:
                time.sleep(self.retry_delay)
                
        logger.error("❌ Всі спроби відправки вичерпано")
        return False

    def validate_webhook_url(self) -> bool:
        """
        Перевіряє доступність webhook URL
        
        Returns:
            True якщо URL доступний, False - інакше
        """
        try:
            response = self.session.get(
                self.webhook_url.replace('/post', '/get') if 'httpbin' in self.webhook_url else self.webhook_url,
                timeout=5
            )
            return response.status_code < 400
        except Exception as e:
            logger.warning(f"⚠️ Не вдалося перевірити webhook URL: {e}")
            return False

    def run(self):
        """
        Основний цикл роботи пристрою
        """
        print(f"🚀 IoT пристрій {self.device_id} запущено")
        print(f"📡 Відправка даних на: {self.webhook_url}")
        print(f"⏱️ Інтервал: {self.interval} секунд")
        print(f"🌡️ Діапазон температури: {self.min_temp}°C - {self.max_temp}°C")
        print("-" * 60)
        
        # Перевірка webhook URL
        if not self.validate_webhook_url():
            logger.warning("⚠️ Webhook URL може бути недоступний")
        
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        try:
            while True:
                try:
                    # Генерація та відправка даних
                    data = self.generate_temperature_data()
                    success = self.send_data(data)
                    
                    if success:
                        consecutive_failures = 0
                    else:
                        consecutive_failures += 1
                        
                    # Перевірка на критичну кількість помилок
                    if consecutive_failures >= max_consecutive_failures:
                        logger.critical(f"🔴 Критична помилка: {consecutive_failures} невдалих спроб поспіль")
                        logger.info("🔄 Перезапуск через 30 секунд...")
                        time.sleep(30)
                        consecutive_failures = 0
                        continue
                        
                    # Затримка перед наступною ітерацією
                    time.sleep(self.interval)
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Отримано сигнал зупинки від користувача")
                    break
                    
                except Exception as e:
                    logger.error(f"💥 Критична помилка в основному циклі: {e}")
                    logger.info("🔄 Перезапуск через 10 секунд...")
                    time.sleep(10)
                    
        except Exception as e:
            logger.critical(f"💀 Фатальна помилка: {e}")
            
        finally:
            self.cleanup()

    def cleanup(self):
        """Очищення ресурсів"""
        logger.info("🧹 Очищення ресурсів...")
        if hasattr(self, 'session'):
            self.session.close()
        logger.info("👋 IoT пристрій зупинено")


def main():
    """Головна функція"""
    # Конфігурація (можна винести в окремий файл config.json)
    config = {
        "webhook_url": "https://httpbin.org/post",  # Замініть на ваш URL
        "device_id": None,  # Автоматично згенерується UUID
        "min_temp": 18.0,
        "max_temp": 32.0,
        "interval": 5
    }
    
    # Створення та запуск пристрою
    device = IoTDevice(
        device_id=config["device_id"],
        webhook_url=config["webhook_url"]
    )
    
    # Налаштування параметрів
    device.min_temp = config["min_temp"]
    device.max_temp = config["max_temp"]
    device.interval = config["interval"]
    
    # Запуск
    device.run()


if __name__ == "__main__":
    main()