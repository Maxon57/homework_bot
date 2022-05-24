import os
import time
from http import HTTPStatus

import requests
from telegram import Bot

from dotenv import load_dotenv

from exeptions import ExceptionVariablesEnvironment

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    return bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """
    Делает запрос к единственному эндпоинту API-сервиса.
    Возвращает ответ API
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code == HTTPStatus.OK:
        return response.json()


def check_response(response) -> list:
    """
    Проверяет ответ API на корректность.
    Возввращает список домашних работ.
    """
    if 'homeworks' in response:
        return response.get('homeworks')


def parse_status(homework):
    """
    Извлекает из информации о конкретной домашней
    работе статус этой работы. Возвращает подготовленную
    для отправки в Telegram строку.
    """
    if bool(homework):
        homework_name = homework[0].get('homework_name')
        homework_status = homework[0].get('status')
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        return 'Работа еще не загружена'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    SECRET_DATA = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(SECRET_DATA)


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        raise ExceptionVariablesEnvironment(
            'Проверьте переменное окружение!'
        )
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            list_homeworks = check_response(response)
            string_response = parse_status(list_homeworks)
            send_message(bot, string_response)
            current_timestamp = int(time.time()) + RETRY_TIME
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            pass


if __name__ == '__main__':
    main()
