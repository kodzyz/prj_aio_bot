from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

# класс-шаблон с данными, отправляемыми в запросе обратного вызова
product_cb = CallbackData('product', 'id', 'action')


# РЕАЛИЗУЕМ КОРЗИНУ

# 4.3 реализуем обработчик формирования разметки для товара в корзине
# будет блок где сможем менять количество любого товара в корзине (у4-с9)
# Листинг 4.7. step_4 /keyboards/inline/products_from_cart.py
def product_markup(idx, count):
    global product_cb

    markup = InlineKeyboardMarkup()
    # Создаем объект клавиатуры

    back_btn = InlineKeyboardButton('⬅',
                                    callback_data=product_cb.new(id=idx,
                                                                 action='decrease'))
    # Кнопка уменьшения количества товара в заказе
    # обработчик к кнопке (action='decrease')

    count_btn = InlineKeyboardButton(count,
                                     callback_data=product_cb.new(id=idx,
                                                                  action='count'))
    # Отображения количества товара

    next_btn = InlineKeyboardButton('➡',
                                    callback_data=product_cb.new(id=idx,
                                                                 action='increase'))
    # Кнопка увеличения количества товара в заказе

    markup.row(back_btn, count_btn, next_btn)
    # Добавляем кнопки в клавиатуру

    return markup
    # возвращаем объект клавиатуры


# следующий щаг handlers/user/cart.py
# 4.4 реализуем обработчик вывода содержимого корзины
