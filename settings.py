from typing import Dict, List, Union

RETRY_TIME = 600

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

CustomDict = Dict[str, Union[List[Dict[str, Union[int, str]]], int]]
CustomList = Union[
    List[Dict[str, Union[str, int]]],
    Dict[str, Union[str, int]]
]
