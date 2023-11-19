# Урок 4. Создаем каталог и корзину пользователя

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from loader import db

# создаем класс-шаблон с данными, отправляемыми в запросе обратного вызова
category_cb = CallbackData('category', 'id', 'action')
# по 'id'-категории будем брать товары категории из бд


# 4.1 реализуем обработчик формирования разметки для списка категорий
# выводим все категории из бд
# Листинг 4.1. step_4 /keyboards/inline/categories.py
def categories_markup():
    '''вывод набора категорий
    каждая категория это кнопка для получения товаров
    входящих в нее'''
    global category_cb

    # Создаем разметку клавиатуры
    markup = InlineKeyboardMarkup()

    # Получаем список категорий из базы данных
    for idx, title in db.fetchall('SELECT * FROM categories'):
        markup.add(InlineKeyboardButton(title,
                                        callback_data=category_cb.new(id=idx,
                                                                      action='view')))
    # для каждой категории создаем кнопку
    # При нажатии на кнопку(выбор категории)
    # будет создаваться новый объект класса CallbackData,
    # отправляемыми в запросе обратного вызова
    # В эти данные будем записывать id категории

    # action='view' ->
    # привяжем к каждой кнопке категории обработчик вывода списка товаров категории
    # handlers/user/catalog.py -> def category_callback_handler()

    return markup


# 4.2 реализуем обработчик вывода списка товаров категории

# получение набора товаров при нажатии на кнопку списка категории
# Перейдем в директорию handlers/user и добавим модуль catalog.py















