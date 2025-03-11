from psychopy import visual, event, core
import os
import random
import csv
import requests

# Конфігурація блоків
block_configurations = [
    {'purple': 50, 'blue': 50, 'repeat_blue': 0},
    {'purple': 50, 'blue': 50, 'repeat_blue': 0},
    {'purple': 40, 'blue': 60, 'repeat_blue': 10},
    {'purple': 28, 'blue': 72, 'repeat_blue': 22},
    {'purple': 16, 'blue': 84, 'repeat_blue': 34},
    {'purple': 16, 'blue': 84, 'repeat_blue': 34},
    {'purple': 6, 'blue': 94, 'repeat_blue': 44},
    {'purple': 6, 'blue': 94, 'repeat_blue': 44}
]

stimuli_path = r"C:\Users\basht\Desktop\ТОЧКИ"
break_images = [
    os.path.join(stimuli_path, f"кар{i}.jpg") for i in range(1, 7)
] + [os.path.join(stimuli_path, "кар1.jpg")]
break_messages = [
    "Вітаємо ви пройшли перший блок, залишилося всього 7, у вас є час перепочити 30 секунд",
    "Вітаємо ви пройшли два блоки, залишилося всього 6, у вас є час перепочити 30 секунд",
    "Вітаємо ви пройшли три блоки, залишилося всього 5, у вас є час перепочити 30 секунд",
    "Вітаємо ви пройшли чотири блоки, залишилося всього 4, у вас є час перепочити 30 секунд"
    "Вітаємо ви пройшли п'ять блоків, залишилося всього 3, у вас є час перепочити 30 секунд"
    "Вітаємо ви пройшли шість блоків, залишилося всього 2, у вас є час перепочити 30 секунд"
    "Вітаємо ви пройшли сім блоків, залишився всього 1, у вас є час перепочити 30 секунд"
]

# Вікно
win = visual.Window(size=[800, 600], color="white", units="pix")

# Створення файлу для запису результатів
results_file = "results.csv"
with open(results_file, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["block", "trial", "actual_color", "response"])

def send_results(data):
    try:
        response = requests.post("https://color-dots-production.up.railway.app/save_data", json=data)
        response.raise_for_status()  # Це допоможе викликати помилку при неуспішному запиті
        print("Дані успішно відправлено")
    except requests.exceptions.RequestException as e:
        print(f"Помилка при відправці даних: {e}")

def generate_stimuli_filenames(purple_count, blue_count, repeat_blue):
    purple_stimuli = [f"К{i}.jpg" for i in range(1, 51)]
    blue_stimuli = [f"К{i}.jpg" for i in range(51, 101)]
    selected_blue = random.sample(blue_stimuli, blue_count - repeat_blue)
    repeated_blue = random.choices(blue_stimuli, k=repeat_blue)
    stimuli = random.sample(purple_stimuli, purple_count) + selected_blue + repeated_blue
    random.shuffle(stimuli)
    return stimuli

trial_counter = 0
for block_num, config in enumerate(block_configurations):
    block_data = []
    
    for filename in generate_stimuli_filenames(config['purple'], config['blue'], config['repeat_blue']):
        trial_counter += 1
        actual_color = "blue" if int(filename[1:-4]) > 50 else "purple"
        
        # Очікування відповіді учасника
        response = None
        while response not in ['blue', 'purple']:  # Очікуємо натискання клавіші
            response = event.waitKeys(keyList=['blue', 'purple'])[0]  # Чекаємо натискання 'blue' або 'purple'
        
        # Додаємо дані до списку
        block_data.append({
            "block": block_num + 1,
            "trial": trial_counter,
            "actual_color": actual_color,
            "response": response
        })
    
    # Відправка результатів на сервер
    send_results(block_data)
    
    # Перерва після кожного блоку
    if block_num < len(block_configurations) - 1:
        for i, img in enumerate(break_images):
            break_message = break_messages[i] if i < len(break_messages) else "Продовжимо через 30 секунд"
            message = visual.TextStim(win, text=break_message, color="black")
            message.draw()
            win.flip()
            core.wait(30)

