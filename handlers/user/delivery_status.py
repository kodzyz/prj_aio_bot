from aiogram.types import Message

from loader import db, dp
from .menu import delivery_status  # '🚚 Статус заказа'
from filters import IsUser


# СТАТУС ЗАКАЗА

# Листинг 16. /handlers/user/cart.py

# 5.12 реализуем отображение активных заказов
# (у5-с13)
# Листинг 5.17. step_5 /handlers/user/delivery_status.py
@dp.message_handler(IsUser(), text=delivery_status)
async def process_delivery_status(message: Message):
    ''':text=delivery_status: запуск ф-ции
     при нажатии на кнопку'''

    orders = db.fetchall('SELECT * FROM orders WHERE cid=?',
                         (message.chat.id,))
    # Получаем содержимое из таблицы заказов по id пользователя

    if len(orders) == 0:
        await message.answer('У вас нет активных заказов.')
    else:
        await delivery_status_answer(message, orders)
        # функции отображения статуса заказа


# Листинг 5.18. step_5 /handlers/user/delivery_status.py
async def delivery_status_answer(message, orders):
    '''функция отображения статуса заказа'''

    res = ''

    for order in orders:
        res += f'Заказ <b>№{order[3]}</b>'
        answer = [
            ' лежит на складе.',
            ' уже в пути!',
            ' прибыл и ждет вас на почте!'
        ]

        res += answer[0]
        res += '\n\n'

    await message.answer(res)
# Пример ответа:
# Заказ №21b4193fe681c7ed7467d9f7c53774b0=3 лежит на складе.


# Подключим обработчики к нашему проекту
# Листинг 19. /handlers/user/__init__.py


# Работа с заказом на стороне админа
# (у5-с15)
# Листинг 20. /handlers/admin/orders.py
