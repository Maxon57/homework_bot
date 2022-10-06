# homework_bot
**Описание**

Бот делает запрос к API сервиса Яндекс.Практикум 
для получения информации о текущем статусе домашней работы.

**Технологии**

Python 3.7
Python-telegram-bot 13.7

**Создание бота в Telegram**
- создайте бота в telegram([см. официальную документацию](https://core.telegram.org/bots)) и 
получите token,
- узнайте свой chat_id,
- создайте файл .env и занесите данные вашего chat_id, token и practicum_token
для переменного окружения (пример в файле .env.example)

**Запуск проекта в dev-режиме**
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Maxon57/homework_bot.git
```
Создать и активировать виртуальное окружение:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
```
python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Запустить проект:
```
python3 homewok.py runserver
```

**Авторы**

* [Максим Игнатов](https://github.com/Maxon57)
