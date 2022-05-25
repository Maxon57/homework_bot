import os
import time
from http import HTTPStatus

import requests
import telegram
from telegram import Bot

from dotenv import load_dotenv

from exeptions import ExceptionVariablesEnvironment
from typing import Union, Dict, List

from logger import logger

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/j'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
bot = Bot(token=TELEGRAM_TOKEN)
CustomDict = Dict[str, Union[List[Dict[str, Union[int, str]]], int]]
CustomList = List[Dict[str, Union[str, int]]]


def send_message(message: str) -> telegram.Bot.send_message:
    """Отправляет сообщение в Telegram чат."""
    return bot.send_message(TELEGRAM_CHAT_ID, message)


def send_error_message(message_err: str) -> None:
    """Отправялет сообщения в логи и в Telegram."""
    logger.error(message_err + u'\u26A0\uFE0F')
    logger.info(f'''Информация о текущем состоянии
                отправлено боту: {bot.first_name}''')
    send_message(message_err)


def get_api_answer(current_timestamp: int) -> CustomDict:
    """
    Делает запрос к единственному эндпоинту API-сервиса.
    Возвращает ответ API.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    valid_response = None
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
            timeout=5
        )
        if response.status_code != HTTPStatus.OK:
            message = 'Сервер домашки не отправил статус 200!'
            send_error_message(message)
            return {}
        valid_response = response
    except requests.exceptions.HTTPError:
        message_err = f'''Сбой в работе программы:
        Эндпоинт {valid_response.url} недоступен.
        Код ответа API: 404'''
        send_error_message(message_err)
    except requests.exceptions.ReadTimeout:
        message_err = f'''Сбой в работе программы:
           сервер не отправил никаких данных за отведенное время'''
        send_error_message(message_err)
    except requests.exceptions.ConnectionError:
        message_err = f'''Сбой в работе программы:
           Произошла ошибка подключения. Проверить подлкючение к интернету'''
        send_error_message(message_err)

    return valid_response.json()


def check_response(response: CustomDict) -> CustomList:
    """
    Проверяет ответ API на корректность.
    Возввращает список домашних работ.
    """
    if 'homeworks' not in response:
        message_err = 'В словаре отсутствует ключ - homeworks'
        send_error_message(message_err)
    return response.get('homeworks')


def parse_status(homework: CustomList) -> str:
    """
    Извлекает из информации о конкретной домашней
    работе статус этой работы. Возвращает подготовленную
    для отправки в Telegram строку.
    """
    homework_name = homework[0].get('homework_name', 'Noname work')
    try:
        homework_status = homework[0].get('status')
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError:
        message_err = ('''Ошибка ключа или во входном homework'
                       или в глобальном HOMEWORK_STATUSES''')
        send_error_message(message_err)
        return (f'На запрос статуса работы "{homework_name}" '
                'получен неизвестный статус.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    SECRET_DATA = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(SECRET_DATA)


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical(f'''Отсутсвует(ют) переменная(ые) окружения.
                   Программа принудительно остановлена''')
        raise ExceptionVariablesEnvironment(
            'Проверьте переменные окружение!'
        )

    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            list_homeworks = check_response(response)
            string_response = parse_status(list_homeworks)
            send_message(string_response)
            current_timestamp = int(time.time()) + RETRY_TIME
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(message)
            time.sleep(RETRY_TIME)
        else:
            pass


if __name__ == '__main__':
    main()
