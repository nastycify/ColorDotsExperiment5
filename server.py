from flask import Flask, request, send_from_directory, jsonify
import os
import openpyxl
from openpyxl import Workbook
import logging

# Створення папки для тимчасових файлів, якщо її ще немає
tmp_folder = 'tmp'  # Назва папки для тимчасових файлів
if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)  # Створення папки, якщо її немає

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
    try:
        data = request.get_json()

        # Логування отриманих даних
        app.logger.info(f"Received data: {data}")

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Перевірка структури вхідних даних
        required_fields = ["name", "color", "response"]
        for item in data:
            if not all(field in item for field in required_fields):
                return jsonify({"error": f"Missing required fields in entry: {item}"}), 400

        # Створення або оновлення файлу з результатами
        file_path = os.path.join(tmp_folder, 'results.xlsx')  # Шлях до файлу в tmp

        if os.path.exists(file_path):
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
        else:
            wb = Workbook()
            sheet = wb.active
            sheet.append(["Name", "Color", "Response"])  # Оновлено заголовки

        # Додавання нових даних
        for item in data:
            sheet.append([
                item.get("name"),
                item.get("color"),
                item.get("response")
            ])

        # Збереження Excel-файлу
        wb.save(file_path)

        app.logger.info("Data successfully saved")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        app.logger.error(f"Error saving data to Excel: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Завантаження результатів
@app.route('/download_results')
def download_results():
    app.logger.info("Downloading results.xlsx")
    try:
        return send_from_directory(tmp_folder, 'results.xlsx', as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error downloading results: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Запуск сервера на порту 8000 (потрібно для Railway)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
