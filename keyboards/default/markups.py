# 3.15 реализуем модуль с функциями формирования разметки клавиатуры
#
# В модуле add.py есть функции back_markup, check_markup
# отвечающие за формирование клавиатуры.
# Они не относятся непосредственно к логике проекта,
# поэтому вынесем их в отдельный модуль keyboards.


from aiogram.types import ReplyKeyboardMarkup

back_message = '👈 Назад'
all_right_message = '✅ Все верно'
cancel_message = '🚫 Отменить'
confirm_message = '✅ Подтвердить заказ'


# Листинг 3.31. step_3 /keyboards/default/markups.py
def back_markup():
    '''разметка для возврата к вводу названия'''
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    # selective=True - выборачная разметка, только для IsAdmin

    markup.add(back_message)
    # кнопка отмены
    # обработчик process_title_back

    return markup


def check_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, all_right_message)

    return markup


# Листинг 5.13. step_5 /keyboards/default/markups.py
# (урок 5-стр 10)
def confirm_markup():
    '''ф-я формирования разметки для подтверждения заказа.
    # используется в - Листинг 12. /handlers/user/cart.py
    # (у5-с10)'''
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(confirm_message)
    markup.add(back_message)

    return markup


# Урок 6. Реализуем подсистему вопросов

# предыдущее:
# Листинг 3. step_6 /handlers/user/sos.py
# Листинг 4. step_6 /handlers/user/__init__.py

# ф-я для формирования разметки клавиатуры
# подтверждение вопроса пользователя
# Листинг 6.5. step_6 /keyboards/default/markups.py
def submit_markup():
    '''ф-я подтверждения,
    что все введено верно'''

    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(cancel_message, all_right_message)

    return markup

# следующее:
# Листинг 6. step_6 /handlers/user/sos.py
