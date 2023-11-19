# Суть фильтров такова, что, когда мы получаем сообщение,
# нам нужно запустить соответствующий обработчик.
# Но нам нужно запустить именно нужный обработчик.
# У обработчиков могут быть свои фильтры,
# если какой-то из фильтров сработал,
# то запускается код из тела обработчика.

from aiogram.types import Message
# специальный класс для создания своих классов-фильтров
from aiogram.dispatcher.filters import BoundFilter
from data.config import ADMINS


class IsAdmin(BoundFilter):

    async def check(self, message: Message):
        '''
        асинхронный метод проверки
        зашел ли текущий пользователь
        под режимом администратора
        '''

        # id пользователя отправившего сообщение
        return message.from_user.id in ADMINS
