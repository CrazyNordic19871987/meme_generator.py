# 🎯 Умный генератор обучающих мемов

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Генератор мемов для создания обучающих материалов с использованием искусственного интеллекта и популярных мем-шаблонов.

## ✨ Возможности

- 🎨 **Создание локальных мемов** - красивый дизайн с тематическим оформлением
- 🌐 **Онлайн-генерация** - использование популярных шаблонов через Imgflip API
- 🤖 **ИИ-генерация текста** - интеграция с Ollama для умных подписей
- 💾 **Сохранение мемов** - экспорт в PNG формате
- 🎯 **Тематические шаблоны** - автоматическое определение темы (математика, физика, программирование и др.)

## 🚀 Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt

Запуск приложения
bash
python meme_generator.py
⚙️ Настройка
Для онлайн-мемов (Imgflip)
Зарегистрируйтесь на imgflip.com

В файле meme_generator.py замените:

python
self.imgflip_username = "your_username"
self.imgflip_password = "your_password"
Для ИИ-генерации (Ollama)
Установите Ollama

Загрузите модель:

bash
ollama pull llama3.1
Запустите сервер:

bash
ollama serve
🎮 Использование
Введите тему, которую не понимаете

Выберите режим генерации:

🎨 Локальный - быстрые мемы с красивым дизайном

🌐 Онлайн - популярные мем-шаблоны

Нажмите "Сгенерировать"

Сохраните понравившийся мем

📸 Примеры
https://images/example_meme.png

🛠 Технологии
Python 3.8+ - основной язык

Tkinter - графический интерфейс

Pillow (PIL) - работа с изображениями

Requests - HTTP запросы к API

Ollama - локальная языковая модель

📦 Структура проекта
text
meme-generator/
├── meme_generator.py    # Основное приложение
├── requirements.txt     # Зависимости Python
├── README.md           # Документация
├── .gitignore          # Игнорируемые файлы
└── images/             # Примеры и ресурсы
🤝 Вклад в проект
Форкните репозиторий

Создайте ветку для функции (git checkout -b feature/amazing-feature)

Закоммитьте изменения (git commit -m 'Add amazing feature')

Запушьте в ветку (git push origin feature/amazing-feature)

Откройте Pull Request

📄 Лицензия
Этот проект распространяется под лицензией MIT. См. файл LICENSE для подробностей.
