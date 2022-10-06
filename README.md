# homework_bot
***
<details>
    <summary style="font-size: 16pt; font-weight: bold">Описание</summary>
  Бот делает запрос к API сервиса Яндекс.Практикум 
для получения информации о текущем статусе домашней работы.
</details>

***
<details>
    <summary style="font-size: 16pt; font-weight: bold">Технологии</summary>

* Python 3.7
* Python-telegram-bot 13.7

</details>

*** 
<details>
    <summary style="font-size: 16pt; font-weight: bold">Создание бота в Telegram</summary>

* создайте бота в telegram ([см. официальную документацию](https://core.telegram.org/bots)) и 
получите token, 
* узнайте свой chat_id, 
* *создайте файл .env и занесите данные вашего chat_id, token и practicum_token
для переменного окружения (пример в файле .env.example)
</details>

****
<details>
    <summary style="font-size: 16pt; font-weight: bold">Запуск проекта</summary>
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
</details>

***
<details>
    <summary style="font-size: 16pt; font-weight: bold">Авторы</summary>

  * [Максим Игнатов](https://github.com/Maxon57)
</details>



