from flask import Flask, request, send_from_directory, jsonify
import os
import openpyxl
from openpyxl import Workbook
import logging

# Створення екземпляра Flask
app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Показ експерименту
@app.route('/')
def serve_experiment():
    app.logger.info("Serving experiment page")
    return send_from_directory('templates', 'index.html')

# Показ таблиць, зображень та інших ресурсів
@app.route('/static/<path:filename>')
def serve_resources(filename):
    app.logger.info(f"Serving resource: {filename}")
    return send_from_directory('static', filename)

# Прийом даних від респондентів та збереження у .xlsx
@app.route('/submit_results', methods=['POST'])
def submit_results():
    data = request.get_json()  # Отримання JSON-даних з експерименту

    if not data:
        return jsonify({"error": "No data received"}), 400

    # Створення або оновлення файлу з результатами
    file_path = 'results.xlsx'

    # Створення нового робочого листа або завантаження існуючого
    try:
        if os.path.exists(file_path):
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active  # Використовуємо перший лист
        else:
            wb = Workbook()  # Створення нового файлу, якщо він не існує
            sheet = wb.active
            sheet.append(["Name", "Stimul", "Color"])  # Ініціалізуємо заголовки

        # Додавання нових даних
        # Приймаємо дані як список об'єктів
        if isinstance(data, list):
            for item in data:
                sheet.append([item.get("name"), item.get("stimul"), item.get("color")])  # Вставка даних
        else:
            sheet.append([data.get("name"), data.get("stimul"), data.get("color")])  # Вставка одного запису

        # Збереження Excel-файлу
        wb.save(file_path)

        app.logger.info(f"Data saved: {data}")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        app.logger.error(f"Error saving data to Excel: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Завантаження результатів
@app.route('/download_results')
def download_results():
    app.logger.info("Downloading results.xlsx")
    try:
        return send_from_directory('.', 'results.xlsx', as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error downloading results: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Запуск сервера на порту 8000 (потрібно для Railway)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))  # Використовуємо порт, наданий Railway
    app.run(host='0.0.0.0', port=port, debug=True)


