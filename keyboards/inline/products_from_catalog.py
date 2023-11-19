from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loader import db

# создаем класс-шаблон с данными, отправляемыми в запросе обратного вызова
product_cb = CallbackData('product', 'id', 'action')


# Листинг 4.5. step_4 /keyboards/inline/products_from_catalog.py
def product_markup(idx='', price=0):
    '''Для каждого товара будет создана кнопка с указанием цены
    По этой кнопке сможем добавить товар в корзину
    К кнопке привязываем обработчик action='add' '''
    global product_cb

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f'Добавить в корзину - {price}₽',
                                    callback_data=product_cb.new(id=idx,
                                                                 action='add')))
    # обработчик action='add' -> handlers/user/catalog.py add_product_callback_handler()

    return markup
