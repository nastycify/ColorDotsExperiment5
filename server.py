from flask import Flask, request, send_from_directory, jsonify
import os
import pandas as pd  # Бібліотека для роботи з Excel
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
    new_data = pd.DataFrame([data])  # Конвертація отриманих даних у DataFrame

    if os.path.exists(file_path):
        existing_data = pd.read_excel(file_path)
        new_data = pd.concat([existing_data, new_data], ignore_index=True)

    # Збереження даних у файл Excel
    new_data.to_excel(file_path, index=False)

    app.logger.info(f"Data saved: {data}")
    return jsonify({"status": "success"}), 200

# Завантаження результатів
@app.route('/download_results')
def download_results():
    app.logger.info("Downloading results.xlsx")
    return send_from_directory('.', 'results.xlsx', as_attachment=True)

# Запуск сервера на порту 8000 (потрібно для Railway)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))  # Використовуємо порт, наданий Railway
    app.run(host='0.0.0.0', port=port, debug=True)


