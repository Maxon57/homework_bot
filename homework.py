import logging
import os
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv
from telegram import Bot

from exeptions import BotException
from settings import (ENDPOINT, HOMEWORK_STATUSES, RETRY_TIME, CustomDict,
                      CustomList)

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
CACHE = {}

logger = logging.getLogger(__name__)
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


def send_message(bot: Bot, message: str) -> Bot.send_message:
    """Отправляет сообщение в Telegram чат."""
    try:
        send_mess = bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Информация о текущем состоянии отправлено боту.')
    except telegram.TelegramError:
        raise BotException('Ошибка отправки сообщения в Telegram!')
    return send_mess


def get_api_answer(current_timestamp: int) -> CustomDict:
    """
    Делает запрос к единственному эндпоинту API-сервиса.
    Возвращает ответ API.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params,
        )
    except requests.exceptions.RequestException as err:
        message_err = f'Не удалось подключиться. Возникла ошибка: {err}'
        raise BotException(message_err)

    if response.status_code != HTTPStatus.OK:
        message_err = f'''Эндпоинт {response.url} недоступен.
        Код ответа API: {response.status_code}
        '''
        raise BotException(message_err)

    return response.json()


def check_response(response: CustomDict) -> CustomList:
    """
    Проверяет ответ API на корректность.
    Возвращает список домашних работ.
    """
    if 'homeworks' not in response:
        message_err = 'Из ответа API нет ключа "homework"!'
        raise TypeError(message_err)

    list_hw = response['homeworks']

    if not isinstance(list_hw, list):
        message_err = 'В homeworks пришел не список!'
        raise BotException(message_err)
    if not list_hw:
        message_err = 'В homeworks пустой список!'
        raise BotException(message_err)

    return list_hw


def parse_status(homework: CustomList) -> str:
    """
    Извлекает из информации о конкретной домашней работе.
    Возвращает подготовленную для отправки в Telegram строку.
    """
    if 'homework_name' in homework:
        homework_name = homework['homework_name']
    else:
        message_err = 'В homework_name отсутствует имя'
        raise KeyError(message_err)

    homework_status = homework.get('status')

    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError:
        message_err = (f'''На запрос работы "{homework_name}"
                получен неизвестный статус {homework_status}.''')
        raise BotException(message_err)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    SECRET_DATA = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(SECRET_DATA)


def cache_err(message_err: str) -> str:
    """
    Проверяет наличие значений в КЭШ.
    Если есть то не отправляет повторно данные.
    """
    global CACHE
    if message_err not in CACHE:
        CACHE[message_err] = message_err
        return message_err


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('''Отсутствует(ют) переменная(ые) окружения.
        Программа принудительно остановлена.''')
        raise BotException(
            'Проверьте переменные окружения!'
        )
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            list_hw = check_response(response)
            for homework in list_hw:
                message = parse_status(homework)
                send_message(bot, message)
            current_timestamp = int(time.time())
        except BotException as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if cache_err(message):
                send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(error)
            if cache_err(message):
                send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
