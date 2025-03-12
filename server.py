from flask import Flask, request, send_from_directory, jsonify
import os
import csv

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

# Показ експерименту
@app.route('/')
def serve_experiment():
    # Відкриває файл index.html як головну сторінку
    return send_from_directory('templates', 'index.html')

# Показ таблиць, зображень та інших ресурсів
@app.route('/static/<path:filename>')
def serve_resources(filename):
    return send_from_directory('static', filename)

# Прийом даних від респондентів
@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.get_json()  # Отримання JSON-даних з експерименту

    # Створення (або доповнення) файлу для збереження результатів
    file_path = 'results.csv'
    with open(file_path, 'a', newline='') as f:
        # Визначення заголовків для CSV-файлу
        writer = csv.DictWriter(f, fieldnames=['participant', 'stimulus_name', 'stimulus_color', 'response'])

        # Якщо файл порожній, додати заголовки
        if f.tell() == 0:
            writer.writeheader()

        # Запис даних у файл
        writer.writerow(data)

    # Повертає відповідь "success", щоб показати, що все працює
    return jsonify({"status": "success"}), 200

# Завантаження результатів
@app.route('/download_results')
def download_results():
    return send_from_directory('.', 'results.csv', as_attachment=True)

# Запуск сервера на порту 8000 (потрібно для Railway)
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))  # Використовуємо порт, наданий Railway
    app.run(host='0.0.0.0', port=port, debug=True)
