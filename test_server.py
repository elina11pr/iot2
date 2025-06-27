#!/usr/bin/env python3
"""
Тестовий Flask сервер для прийому даних від IoT пристроїв
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import logging

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Зберігання отриманих даних в пам'яті
received_data = []

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обробник webhook для отримання даних від IoT пристроїв"""
    try:
        # Отримання JSON даних
        data = request.get_json()
        
        if not data:
            logger.warning("Отримано порожні дані")
            return jsonify({
                "status": "error", 
                "message": "Порожні дані"
            }), 400
        
        # Валідація обов'язкових полів
        required_fields = ['device_id', 'temperature', 'timestamp']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            logger.warning(f"Відсутні поля: {missing_fields}")
            return jsonify({
                "status": "error",
                "message": f"Відсутні обов'язкові поля: {missing_fields}"
            }), 400
        
        # Валідація типів даних
        try:
            temperature = float(data['temperature'])
            if not isinstance(data['device_id'], str) or not data['device_id'].strip():
                raise ValueError("device_id повинен бути непорожнім рядком")
        except (ValueError, TypeError) as e:
            logger.warning(f"Невірний формат даних: {e}")
            return jsonify({
                "status": "error",
                "message": f"Невірний формат даних: {e}"
            }), 400
        
        # Додавання часу отримання
        data['received_at'] = datetime.now().isoformat()
        
        # Збереження даних
        received_data.append(data)
        
        # Логування
        logger.info(f"📨 Отримано дані від {data['device_id']}: {temperature}°C")
        
        # Відповідь клієнту
        response = {
            "status": "success",
            "message": "Дані успішно отримано",
            "received_at": data['received_at'],
            "data_count": len(received_data)
        }
        
        return jsonify(response), 200
        
    except json.JSONDecodeError:
        logger.error("Помилка декодування JSON")
        return jsonify({
            "status": "error",
            "message": "Невірний JSON формат"
        }), 400
        
    except Exception as e:
        logger.error(f"Неочікувана помилка: {e}")
        return jsonify({
            "status": "error",
            "message": "Внутрішня помилка сервера"
        }), 500

@app.route('/data', methods=['GET'])
def get_data():
    """Отримання всіх збережених даних"""
    try:
        device_id = request.args.get('device_id')
        limit = request.args.get('limit', type=int)
        
        # Фільтрація за device_id
        filtered_data = received_data
        if device_id:
            filtered_data = [d for d in received_data if d.get('device_id') == device_id]
        
        # Обмеження кількості записів
        if limit and limit > 0:
            filtered_data = filtered_data[-limit:]
        
        return jsonify({
            "status": "success",
            "total_count": len(received_data),
            "filtered_count": len(filtered_data),
            "data": filtered_data
        }), 200
        
    except Exception as e:
        logger.error(f"Помилка при отриманні даних: {e}")
        return jsonify({
            "status": "error",
            "message": "Помилка при отриманні даних"
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Статистика отриманих даних"""
    try:
        if not received_data:
            return jsonify({
                "status": "success",
                "message": "Немає даних",
                "stats": {}
            }), 200
        
        # Підрахунок статистики
        devices = set(d.get('device_id') for d in received_data)
        temperatures = [float(d.get('temperature', 0)) for d in received_data if 'temperature' in d]
        
        stats = {
            "total_records": len(received_data),
            "unique_devices": len(devices),
            "devices": list(devices),
            "temperature_stats": {
                "min": min(temperatures) if temperatures else 0,
                "max": max(temperatures) if temperatures else 0,
                "avg": sum(temperatures) / len(temperatures) if temperatures else 0,
                "count": len(temperatures)
            }
        }
        
        return jsonify({
            "status": "success",
            "stats": stats
        }), 200
        
    except Exception as e:
        logger.error(f"Помилка при обчисленні статистики: {e}")
        return jsonify({
            "status": "error",
            "message": "Помилка при обчисленні статистики"
        }), 500

@app.route('/clear', methods=['POST'])
def clear_data():
    """Очищення всіх збережених даних"""
    global received_data
    try:
        count = len(received_data)
        received_data.clear()
        logger.info(f"🧹 Очищено {count} записів")
        
        return jsonify({
            "status": "success",
            "message": f"Очищено {count} записів"
        }), 200
        
    except Exception as e:
        logger.error(f"Помилка при очищенні даних: {e}")
        return jsonify({
            "status": "error",
            "message": "Помилка при очищенні даних"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Перевірка стану сервера"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "records_count": len(received_data)
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Endpoint не знайдено"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "status": "error",
        "message": "HTTP метод не дозволено"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Внутрішня помилка сервера"
    }), 500

if __name__ == '__main__':
    print("🚀 Запуск тестового сервера...")
    print("📡 Доступні endpoints:")
    print("  POST /webhook - Прийом даних від IoT пристроїв")
    print("  GET  /data    - Перегляд збережених даних")
    print("  GET  /stats   - Статистика")
    print("  POST /clear   - Очищення даних")
    print("  GET  /health  - Перевірка стану")
    print("-" * 50)
    
    # Запуск сервера
    app.run(
        host='0.0.0.0',  # Доступ з будь-якої IP
        port=5000,
        debug=True,      # Режим розробки
        threaded=True    # Підтримка багатьох одночасних запитів
    )