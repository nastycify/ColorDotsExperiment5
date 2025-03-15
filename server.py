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
@app.route('/submit_results/<string:loop_name>', methods=['POST'])
def submit_results(loop_name):
    try:
        data = request.get_json()

        # Логування отриманих даних
        app.logger.info(f"Received data for loop {loop_name}: {data}")

        if not data:
            return jsonify({"error": "No data received"}), 400

        # Перевірка структури вхідних даних
        required_fields = ["name", "stimul", "color", "response", "trialNumber"]
        for item in data:
            if not all(field in item for field in required_fields):
                return jsonify({"error": f"Missing required fields in entry: {item}"}), 400

        # Створення або оновлення файлу з результатами в тимчасовій директорії
        file_path = '/tmp/results.xlsx'  # Оновлений шлях

        if os.path.exists(file_path):
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
        else:
            wb = Workbook()
            sheet = wb.active
            sheet.append(["Name", "Stimul", "Color", "Response", "Trial Number", "Loop Name"])

        # Додавання нових даних
        for item in data:
            sheet.append([
                item.get("name"), 
                item.get("stimul"), 
                item.get("color"), 
                item.get("response"), 
                item.get("trialNumber"), 
                loop_name
            ])

        # Збереження Excel-файлу
        wb.save(file_path)

        app.logger.info(f"Data successfully saved for loop {loop_name}")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        app.logger.error(f"Error saving data to Excel: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Завантаження результатів
@app.route('/download_results')
def download_results():
    app.logger.info("Downloading results.xlsx")
    try:
        # Оновлений шлях для завантаження файлу з тимчасової директорії
        return send_from_directory('/tmp', 'results.xlsx', as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error downloading results: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Запуск сервера на порту 8000 (потрібно для Railway)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True)

