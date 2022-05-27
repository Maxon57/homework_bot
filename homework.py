import os
import time
from http import HTTPStatus
from typing import Dict, List, Union

import requests
import telegram
from dotenv import load_dotenv
from emoji import emojize as emoji
from telegram import Bot

from exeptions import ExceptionVariablesEnvironment
import logging
from logging.handlers import RotatingFileHandler
load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 5
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': emoji('''
    :check_mark_button: Работа проверена:
    ревьюеру всё понравилось. Ура!'''
                      ),
    'reviewing': emoji(':memo: Работа взята на проверку ревьюером.'),
    'rejected': emoji('''
    :check_box_with_check: Работа проверена:
    у ревьюера есть замечания.'''
                      )
}
CustomDict = Dict[str, Union[List[Dict[str, Union[int, str]]], int]]
CustomList = Union[
    List[Dict[str, Union[str, int]]],
    Dict[str, Union[str, int]]
]

logger = logging.getLogger('homework')
logger.setLevel(logging.DEBUG)
FORMAT = '%(asctime)s :: %(name)s:%(lineno)s :: %(levelname)s :: %(message)s'
handler = RotatingFileHandler(filename='my_logger.log',
                              maxBytes=5000000,
                              backupCount=5,
                              encoding='utf-8'
                              )
handler.setFormatter(logging.Formatter(FORMAT))
handler.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(FORMAT))
stream_handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(stream_handler)
logger.debug('Приложение бот-ассистент стартовало')


def send_message(bot: Bot, message: str) -> telegram.Bot.send_message:
    """Отправляет сообщение в Telegram чат."""
    return bot.send_message(TELEGRAM_CHAT_ID, message)


def send_error_message(message_err: str) -> None:
    """Отправялет ERROR сообщения в логи и в Telegram."""
    logger.error(message_err)
    logger.info(f'''Информация о текущем состоянии
                отправлено боту.''')
    send_message(main.__dict__['bot'], emoji(f':warning: {message_err}'))


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
        message_err = '''Сбой в работе программы:
        сервер не отправил никаких данных за отведенное время.'''
        send_error_message(message_err)
    except requests.exceptions.ConnectionError:
        message_err = '''Сбой в работе программы:
        Произошла ошибка подключения. Проверьте подключение к интернету.'''
        send_error_message(message_err)
    return valid_response.json()


def check_response(response: CustomDict) -> CustomList:
    """
    Проверяет ответ API на корректность.
    Возвращает список домашних работ.
    """
    if not response:
        message_err = 'От сервера не пришло данных. Пустой словарь!'
        send_error_message(message_err)
    if not bool(response.get('homework')):
        message_err = 'В словаре homeworks пустой список.'
        send_error_message(message_err)
    return response.get('homeworks')


def parse_status(homework: CustomList) -> str:
    """
    Извлекает из информации о конкретной домашней работе.
    Возвращает подготовленную для отправки в Telegram строку.
    """
    homework_name = homework.get('homework_name', 'Noname work')
    try:
        homework_status = homework.get('status')
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError:
        message_err = ('''Ошибка ключа или во входном homework'
                       или в глобальном HOMEWORK_STATUSES''')
        send_error_message(message_err)
        return (f'На запрос статуса работы "{homework_name}" '
                'получен неизвестный статус.')
    return verdict


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    SECRET_DATA = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(SECRET_DATA)


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('''Отсутствует(ют) переменная(ые) окружения.
        Программа принудительно остановлена.''')
        raise ExceptionVariablesEnvironment(
            'Проверьте переменные окружение!'
        )
    bot = Bot(token=TELEGRAM_TOKEN)
    main.bot = bot
    current_timestamp = 1651758808
    while True:
        try:
            response = get_api_answer(current_timestamp)
            if not response:
                time.sleep(RETRY_TIME)
            list_homeworks = check_response(response)
            if not list_homeworks:
                time.sleep(RETRY_TIME)
            if isinstance(list_homeworks, list) and list_homeworks:
                string_response = parse_status(list_homeworks[0])
                logger.info('Бот отправил текущий статус домашки.')
                send_message(bot, string_response)
            time.sleep(RETRY_TIME)
            last_timestapm = response['current_date']
            if last_timestapm:
                current_timestamp = last_timestapm
        except KeyError:
            message_err = 'В ответе API не оказалось "current_date"'
            send_error_message(message_err)
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
