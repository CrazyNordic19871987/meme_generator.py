import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from PIL import Image, ImageDraw, ImageFont, ImageTk
import requests
import random
from datetime import datetime
import os
import threading
from io import BytesIO

class WorkingMemeGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 Умный генератор мемов v4.0")
        self.root.geometry("800x750")
        
        self.ollama_url = "http://localhost:11434"
        self.current_model = "llama3.1"
        self.ai_working = False
        
        # Imgflip API настройки - ЗАМЕНИТЕ НА ВАШИ ДАННЫЕ
        self.imgflip_username = "CrazyNordic"  # ⬅️ ЗАМЕНИТЕ на ваш логин
        self.imgflip_password = "Amsterdam1987!"  # ⬅️ ЗАМЕНИТЕ на ваш пароль
        self.meme_templates = []
        
        # Резервные шаблоны
        self.backup_templates = [
            {'id': '181913649', 'name': 'Drake', 'box_count': 2},
            {'id': '87743020', 'name': 'Two Buttons', 'box_count': 2},
            {'id': '129242436', 'name': 'Change My Mind', 'box_count': 1},
            {'id': '438680', 'name': 'Batman', 'box_count': 2},
            {'id': '188390779', 'name': 'Woman Yelling', 'box_count': 2},
            {'id': '4087833', 'name': 'Waiting Skeleton', 'box_count': 2},
            {'id': '131087935', 'name': 'Running Away Balloon', 'box_count': 2},
            {'id': '217743513', 'name': 'UNO Draw 25', 'box_count': 2},
        ]
        
        self.current_meme_path = None
        self.create_widgets()
        self.check_models()
        self.load_meme_templates()
    
    def load_meme_templates(self):
        """Загружает популярные мем-шаблоны"""
        def load():
            try:
                self.root.after(0, lambda: self.status_var.set("🔄 Загружаю мем-шаблоны..."))
                response = requests.get("https://api.imgflip.com/get_memes", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data['success']:
                        safe_memes = [
                            m for m in data['data']['memes'] 
                            if m['box_count'] <= 3 and 
                            m['id'] in ['181913649', '87743020', '129242436', '438680', 
                                       '188390779', '4087833', '131087935', '217743513']
                        ]
                        self.meme_templates = safe_memes
                        print(f"✅ Загружено {len(safe_memes)} мем-шаблонов")
                        self.root.after(0, lambda: self.templates_var.set(f"✅ Шаблонов: {len(safe_memes)}"))
                    else:
                        self.meme_templates = self.backup_templates
                        self.root.after(0, lambda: self.templates_var.set("✅ Резервные шаблоны"))
                else:
                    self.meme_templates = self.backup_templates
                    self.root.after(0, lambda: self.templates_var.set("✅ Резервные шаблоны"))
            except Exception as e:
                self.meme_templates = self.backup_templates
                self.root.after(0, lambda: self.templates_var.set("✅ Резервные шаблоны"))
                print("✅ Использую резервные шаблоны")
        
        threading.Thread(target=load, daemon=True).start()

    def create_widgets(self):
        # Заголовок
        tk.Label(self.root, text="🎯 Умный генератор мемов", 
                font=("Arial", 18, "bold")).pack(pady=15)
        
        # Информация о моделях
        self.model_var = tk.StringVar(value="🔄 Проверяю модели...")
        model_label = tk.Label(self.root, textvariable=self.model_var, 
                font=("Arial", 10), fg="blue")
        model_label.pack()
        
        # Поле для вопроса
        tk.Label(self.root, text="📝 Опиши, что тебе непонятно:", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        self.question_text = scrolledtext.ScrolledText(self.root, 
                                                     height=4, 
                                                     font=("Arial", 11),
                                                     wrap=tk.WORD)
        self.question_text.pack(fill='x', padx=25, pady=5)
        self.question_text.insert('1.0', "не понимаю теорему Пифагора")
        
        # Примеры запросов
        examples_frame = tk.Frame(self.root)
        examples_frame.pack(pady=5)
        
        examples = [
            "• не понимаю дифференциальные уравнения",
            "• зачем нужны логарифмы в жизни?", 
            "• объясни квантовую физику просто"
        ]
        
        for example in examples:
            tk.Label(examples_frame, text=example, font=("Arial", 9), 
                    fg="gray").pack()
        
        # Режим генерации
        mode_frame = tk.Frame(self.root)
        mode_frame.pack(pady=10)
        
        self.mode_var = tk.StringVar(value="local")
        tk.Radiobutton(mode_frame, text="🌐 Онлайн-мемы (Imgflip)", 
                      variable=self.mode_var, value="online",
                      font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="🎨 Локальные мемы", 
                      variable=self.mode_var, value="local",
                      font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        
        # Кнопка генерации
        self.generate_btn = tk.Button(self.root, text="🚀 Сгенерировать мем-объяснение", 
                                    command=self.start_generation,
                                    font=("Arial", 13, "bold"), 
                                    bg="#2196F3", fg="white",
                                    width=30, height=2)
        self.generate_btn.pack(pady=15)
        
        # Прогресс
        self.status_var = tk.StringVar(value="💡 Введи вопрос и нажми кнопку")
        status_label = tk.Label(self.root, textvariable=self.status_var, 
                font=("Arial", 11))
        status_label.pack()
        
        # Индикатор ИИ
        self.ai_status_var = tk.StringVar(value="")
        ai_status_label = tk.Label(self.root, textvariable=self.ai_status_var, 
                                  font=("Arial", 9), fg="green")
        ai_status_label.pack()
        
        # Информация о шаблонах
        self.templates_var = tk.StringVar(value="📋 Загружаю шаблоны...")
        templates_label = tk.Label(self.root, textvariable=self.templates_var, 
                                  font=("Arial", 9), fg="purple")
        templates_label.pack()
        
        # Область мема с прокруткой
        meme_container = tk.Frame(self.root)
        meme_container.pack(pady=20, padx=25, fill='both', expand=True)
        
        # Создаем Canvas и Scrollbar для мема
        self.canvas = tk.Canvas(meme_container, bg='white', highlightthickness=2, highlightbackground='#2E7D32')
        self.scrollbar = tk.Scrollbar(meme_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Упаковываем canvas и scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Метка для мема внутри прокручиваемой области
        self.meme_label = tk.Label(self.scrollable_frame, 
                                 text="🖼️ Здесь появится твой мем!\n\n"
                                      "ИИ создаст смешное и понятное\nобъяснение любой темы",
                                 font=("Arial", 12), 
                                 bg="white", fg="#666",
                                 justify=tk.CENTER)
        self.meme_label.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Кнопки
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)
        
        self.save_btn = tk.Button(button_frame, text="💾 Сохранить мем", 
                                command=self.save_meme, 
                                state="disabled",
                                font=("Arial", 11),
                                bg="#FF9800", fg="white",
                                width=15)
        self.save_btn.pack(side=tk.LEFT, padx=8)
        
        tk.Button(button_frame, text="🔧 Проверить ИИ", 
                 command=self.test_ai_connection,
                 font=("Arial", 11),
                 bg="#9C27B0", fg="white",
                 width=12).pack(side=tk.LEFT, padx=8)
        
        tk.Button(button_frame, text="🎲 Случайный мем", 
                 command=self.create_random_meme,
                 font=("Arial", 11),
                 bg="#4CAF50", fg="white",
                 width=12).pack(side=tk.LEFT, padx=8)
        
        tk.Button(button_frame, text="🔄 Обновить шаблоны", 
                 command=self.load_meme_templates,
                 font=("Arial", 11),
                 bg="#607D8B", fg="white",
                 width=15).pack(side=tk.LEFT, padx=8)
    
    def check_models(self):
        """Проверяет доступные модели"""
        def check():
            try:
                self.root.after(0, lambda: self.status_var.set("🔍 Проверяю модели..."))
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    if models:
                        model_names = [model['name'] for model in models]
                        self.current_model = model_names[0]
                        model_text = f"✅ Модель: {self.current_model}"
                        self.root.after(0, lambda: self.model_var.set(model_text))
                        self.root.after(0, lambda: self.status_var.set("✅ Готов к работе!"))
                        self.ai_working = True
                    else:
                        self.root.after(0, lambda: self.model_var.set("❌ Нет моделей"))
                        self.root.after(0, lambda: self.status_var.set("✅ Готов (без ИИ)"))
                        self.ai_working = False
                else:
                    self.root.after(0, lambda: self.model_var.set("❌ Ollama не отвечает"))
                    self.root.after(0, lambda: self.status_var.set("✅ Готов (без ИИ)"))
                    self.ai_working = False
            except Exception as e:
                self.root.after(0, lambda: self.model_var.set("❌ Нет подключения к Ollama"))
                self.root.after(0, lambda: self.status_var.set("✅ Готов (без ИИ)"))
                self.ai_working = False
        
        threading.Thread(target=check, daemon=True).start()
    
    def test_ai_connection(self):
        """Тестирует подключение к ИИ"""
        self.status_var.set("🧪 Тестирую ИИ...")
        
        def test():
            try:
                test_prompt = "Привет! Ответь одним словом: 'работает'"
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.current_model,
                        "prompt": test_prompt,
                        "stream": False
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("response", "").strip()
                    self.root.after(0, lambda: self.status_var.set(f"✅ ИИ работает! Ответ: {text[:20]}..."))
                    self.ai_working = True
                else:
                    self.root.after(0, lambda: self.status_var.set("❌ ИИ не отвечает"))
                    self.ai_working = False
                    
            except Exception as e:
                self.root.after(0, lambda: self.status_var.set(f"❌ Ошибка теста: {str(e)}"))
                self.ai_working = False
        
        threading.Thread(target=test, daemon=True).start()
    
    def start_generation(self):
        """Запускает генерацию"""
        question = self.question_text.get('1.0', tk.END).strip()
        if not question or len(question) < 3:
            messagebox.showwarning("Внимание", "📝 Опиши, что тебе непонятно!")
            return
        
        self.generate_btn.config(state="disabled", text="⏳ Обрабатываю...")
        self.status_var.set("🔮 Анализирую вопрос...")
        self.meme_label.configure(text="⏳ Создаю мем...\nПодождите немного...")
        
        thread = threading.Thread(target=self.generate_meme, args=(question,))
        thread.daemon = True
        thread.start()
    
    def generate_meme(self, question):
        """Генерирует мем"""
        try:
            meme_text = None
            
            # Пробуем ИИ если он доступен
            if self.ai_working:
                self.root.after(0, lambda: self.ai_status_var.set("🤖 Использую ИИ..."))
                meme_text = self.try_ai_generation(question)
            
            # Если ИИ не сработал или не доступен
            if not meme_text:
                self.root.after(0, lambda: self.ai_status_var.set("⚡ Упрощенный режим"))
                meme_text = self.create_smart_fallback(question)
            
            # Создаем изображение в зависимости от режима
            self.root.after(0, lambda: self.status_var.set("🎨 Создаю мем..."))
            
            if self.mode_var.get() == "online" and self.meme_templates:
                meme_path = self.create_online_meme(meme_text)
                if not meme_path:
                    self.root.after(0, lambda: self.status_var.set("🔄 Пробую локальный режим..."))
                    meme_path = self.create_local_meme(meme_text)
            else:
                meme_path = self.create_local_meme(meme_text)
            
            if meme_path:
                # Показываем результат
                self.root.after(0, lambda: self.show_result(meme_path, meme_text))
            else:
                self.root.after(0, lambda: self.show_error("❌ Не удалось создать мем"))
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Ошибка: {str(e)}"))
    
    def create_online_meme(self, meme_text):
        """Создает мем через Imgflip API"""
        try:
            if not self.meme_templates:
                return None
                
            template = random.choice(self.meme_templates)
            
            if "|" in meme_text:
                top, bottom = [part.strip() for part in meme_text.split("|", 1)]
            else:
                words = meme_text.split()
                mid = len(words) // 2
                top = ' '.join(words[:mid])
                bottom = ' '.join(words[mid:])
            
            # Пробуем разные аккаунты
            credentials_list = [
                {"username": self.imgflip_username, "password": self.imgflip_password},  # Ваши данные
                {"username": "imgflip_hub", "password": "imgflip_hub"},  # Демо-аккаунт
            ]
            
            for credentials in credentials_list:
                params = {
                    'template_id': template['id'],
                    'username': credentials["username"],
                    'password': credentials["password"],
                    'text0': top[:100],
                    'text1': bottom[:100]
                }
                
                try:
                    response = requests.post("https://api.imgflip.com/caption_image", 
                                           data=params, timeout=15)
                    result = response.json()
                    
                    if result['success']:
                        image_url = result['data']['url']
                        img_response = requests.get(image_url)
                        img = Image.open(BytesIO(img_response.content))
                        
                        meme_path = f"online_meme_{datetime.now().strftime('%H%M%S')}.png"
                        img.save(meme_path, 'PNG')
                        print(f"✅ Онлайн-мем создан: {template['name']}")
                        return meme_path
                    else:
                        print(f"❌ Ошибка Imgflip: {result.get('error_message', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ Ошибка запроса: {e}")
                    continue
            
            print("❌ Все аккаунты не сработали")
            return None
                
        except Exception as e:
            print(f"❌ Ошибка онлайн-генерации: {e}")
            return None
    
    def create_local_meme(self, meme_text):
        """Создает локальный мем"""
        try:
            if "|" in meme_text:
                top, bottom = [part.strip() for part in meme_text.split("|", 1)]
            else:
                top = meme_text
                bottom = "Стало понятнее? 😊"
            
            # Увеличим размер для лучшего отображения
            width, height = 600, 500
            colors = ['#FFEBEE', '#E8F5E8', '#E3F2FD', '#FFF3E0', '#F3E5F5']
            bg_color = random.choice(colors)
            
            image = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(image)
            
            # Шрифты
            try:
                font_large = ImageFont.truetype("arial.ttf", 28)
                font_small = ImageFont.truetype("arial.ttf", 24)
            except:
                try:
                    font_large = ImageFont.truetype("arial.ttf", 28)
                    font_small = ImageFont.truetype("arial.ttf", 24)
                except:
                    font_large = ImageFont.load_default()
                    font_small = ImageFont.load_default()
            
            def draw_text_with_wrap(text, font, y_start, max_width, color='#2E7D32'):
                words = text.split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    text_width = bbox[2] - bbox[0]
                    
                    if text_width <= max_width:
                        current_line.append(word)
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                for i, line in enumerate(lines):
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (width - text_width) // 2
                    y = y_start + i * 35
                    draw.text((x, y), line, font=font, fill=color)
                
                return len(lines)
            
            # Верхний текст
            top_lines = draw_text_with_wrap(top, font_large, 80, width - 80, '#1A237E')
            
            # Разделительная линия
            line_y = 80 + top_lines * 35 + 20
            draw.line([50, line_y, width-50, line_y], fill='#78909C', width=3)
            
            # Нижний текст
            draw_text_with_wrap(bottom, font_small, line_y + 30, width - 80, '#2E7D32')
            
            # Рамка
            draw.rectangle([20, 20, width-20, height-20], outline='#455A64', width=4)
            
            meme_path = f"local_meme_{datetime.now().strftime('%H%M%S')}.png"
            image.save(meme_path, 'PNG')
            
            print("✅ Локальный мем создан")
            return meme_path
            
        except Exception as e:
            print(f"❌ Ошибка создания локального мема: {e}")
            return None
    
    def try_ai_generation(self, question):
        """Пробует сгенерировать текст через ИИ"""
        try:
            prompt = f"""
            Создай смешной мем для объяснения темы: {question}
            Формат: верхний текст | нижний текст
            Пример: "Когда гипотенуза слишком длинная" | "a² + b² = c² - и всё сходится!"
            Только текст в формате: верх | низ
            """
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.current_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                print(f"📨 Ответ ИИ: {text}")
                
                if "|" in text:
                    for line in text.split('\n'):
                        if "|" in line:
                            return line.strip()
                elif text:
                    words = text.split()
                    if len(words) > 3:
                        mid = len(words) // 2
                        return f"{' '.join(words[:mid])} | {' '.join(words[mid:])}"
                
                return text
            else:
                print(f"❌ Ошибка API: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Ошибка ИИ: {e}")
            return None
    
    def create_smart_fallback(self, question):
        """Умный fallback без ИИ"""
        question_lower = question.lower()
        
        if "пифагор" in question_lower or "треугольник" in question_lower:
            templates = [
                "Гипотенуза зовёт гулять, а катеты спят | a² + b² = c² - и ты герой!",
                "Когда в треугольнике всё не так | Квадрат гипотенузы = сумма квадратов катетов ✓",
                "Пытаюсь найти гипотенузу | Катеты в квадрате сложил - и готово! 🎯"
            ]
        elif "математ" in question_lower:
            templates = [
                "Мозг при решении задач | Включил режим 'гений'... или нет? 🤔",
                "Цифры и формулы танцуют | А ответ был так близко! 💡",
            ]
        elif "физик" in question_lower:
            templates = [
                "Законы Ньютона в жизни | Яблоко упало - голова заработала! 🍎",
                "Квантовые частицы и я | И там и тут, пока не посмотрел 👀",
            ]
        elif "хими" in question_lower:
            templates = [
                "Смешиваю вещества в лаборатории | БУМ! Или нет? 🧪",
                "Периодическая таблица Менделеева | H₂O - вода, а дальше... 🤷",
            ]
        elif "программир" in question_lower or "код" in question_lower:
            templates = [
                "Отладка кода | Нашёл баг! Теперь бы починить... 🐛",
                "Изучение Python | Import understanding - успешно! 🐍",
            ]
        else:
            templates = [
                f"Разбираюсь с {question[:20]}... | Оказывается, всё логично! 🧠",
                f"Мозг при изучении {question[:15]} | Перезагрузка... и готово! 🔄",
                f"Когда учитель объясняет {question[:15]} | А я уже всё понял! Нет? 😅"
            ]
        
        return random.choice(templates)
    
    def create_random_meme(self):
        """Создает случайный мем"""
        topics = ["математика", "физика", "программирование", "химия", "биология"]
        topic = random.choice(topics)
        self.question_text.delete('1.0', tk.END)
        self.question_text.insert('1.0', topic)
        self.start_generation()
    
    def show_result(self, meme_path, meme_text):
        """Показывает результат"""
        try:
            # Загружаем изображение
            image = Image.open(meme_path)
            
            # Масштабируем для превью (увеличил размер)
            max_size = (550, 450)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Очищаем предыдущий мем
            self.meme_label.configure(image=photo, text="")
            self.meme_label.image = photo
            
            # Обновляем интерфейс
            self.save_btn.config(state="normal")
            self.generate_btn.config(state="normal", text="🚀 Сгенерировать мем-объяснение")
            self.status_var.set("✅ Мем готов!")
            self.ai_status_var.set("")
            
            self.current_meme_path = meme_path
            
            print(f"🎉 Мем отображен: {meme_text}")
            
        except Exception as e:
            print(f"❌ Ошибка отображения: {e}")
            self.show_error(f"Ошибка отображения: {e}")
    
    def show_error(self, message):
        """Показывает ошибку"""
        messagebox.showerror("Ошибка", message)
        self.status_var.set("❌ Ошибка")
        self.generate_btn.config(state="normal", text="🚀 Сгенерировать мем-объяснение")
        self.ai_status_var.set("")
        self.meme_label.configure(image=None, text="❌ Ошибка создания мема\nПопробуйте еще раз")
    
    def save_meme(self):
        """Сохраняет мем"""
        if hasattr(self, 'current_meme_path') and self.current_meme_path:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                initialfile=f"мем_{datetime.now().strftime('%H%M%S')}.png"
            )
            if filename:
                try:
                    import shutil
                    shutil.copy2(self.current_meme_path, filename)
                    messagebox.showinfo("Успех", f"🎉 Мем сохранен!\n{filename}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def run(self):
        self.root.mainloop()

# Запуск
if __name__ == "__main__":
    print("🎯 Запуск улучшенного генератора мемов...")
    print("💡 Локальный режим всегда работает!")
    print("🔧 Для онлайн-мемов замените логин и пароль в коде")
    app = WorkingMemeGenerator()
    app.run()