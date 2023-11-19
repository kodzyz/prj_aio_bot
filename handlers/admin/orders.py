from aiogram.types import Message

from loader import dp, db
from handlers.user.menu import orders  # '🚚 Заказы'
from filters import IsAdmin


# предыдущее:
# Листинг 18. /handlers/user/delivery_status.py
# Листинг 19. /handlers/user/__init__.py


# 5.13 РЕАЛИЗУЕМ РАБОТУ С ЗАКАЗОМ НА СТОРОНЕ АДМИНА


# обработчик – для отображения списка заказов
# (у5-с15)
# Листинг 5.20. step_5 /handlers/admin/orders.py
@dp.message_handler(IsAdmin(), text=orders)
async def process_orders(message: Message):
    ''':text=: нажатие кнопки 'Заказы' '''

    orders = db.fetchall('SELECT * FROM orders')
    # содержимое таблицы с заказами

    if len(orders) == 0:
        await message.answer('У вас нет заказов.')
    else:
        await orders_answer(message, orders)
        # ф-я – для отображения содержимого заказа


# Листинг 5.21. step_5 /handlers/admin/orders.py
async def orders_answer(message, orders):
    '''отображение содержимого заказа'''

    res = ''

    for order in orders:
        res += f'Заказ <b>№{order[3]}</b>\n\n'

    await message.answer(res)
    # Пример: Заказ №21b4193fe681c7ed7467d9f7c53774b0=3


# Подключим обработчики данного модуля к нашему проекту.
# Листинг 22./handlers/admin/__init__.py
