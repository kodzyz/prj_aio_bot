from aiogram.types import (Message, ReplyKeyboardMarkup,
                           CallbackQuery, ReplyKeyboardRemove)
from aiogram.dispatcher import FSMContext
from aiogram.types.chat import ChatActions
import logging

from filters import IsUser
from loader import db, dp, bot
from .menu import cart  # cart = '🛒 Корзина'
from keyboards.inline.products_from_cart import product_markup
from keyboards.inline.products_from_catalog import product_cb
from states import CheckoutState
from keyboards.default.markups import *


# РЕАЛИЗУЕМ КОРЗИНУ

# 4.4 реализуем обработчик вывода содержимого корзины (у4-с10)
# Листинг 4.8. step_4 /handlers/user/cart.py
@dp.message_handler(IsUser(), text=cart)
async def process_cart(message: Message, state: FSMContext):
    cart_data = db.fetchall(
        'SELECT * FROM cart WHERE cid=?', (message.chat.id,))
    # содержимое корзины по id текущего пользователя

    if len(cart_data) == 0:  # Если корзина пуста

        await message.answer('Ваша корзина пуста.')
    else:

        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        # имитация печати живого человека

        async with state.proxy() as data:
            data['products'] = {}
            # Наполняем вложенный словарь с контекстом
            # 'products' - ключ, значением будет словарь

        order_cost = 0
        # Общая стоимость заказа изначально равняется нулю

        for _, idx, count_in_cart in cart_data:  # Обходим содержимое корзины
            # _ - id клиента (не используется в коде)
            # idx - id товара,
            # count_in_cart - количество

            product = db.fetchone('SELECT * FROM products WHERE idx=?',
                                  (idx,))
            # Получаем сам объект товара по id товара взятого из корзины (idx)

            if product == None:

                db.query('DELETE FROM cart WHERE idx=?', (idx,))
                # Возможно товара уже в каталоге нет,
                # значит нужно его удалить и из корзины

            else:
                _, title, body, image, price, _ = product
                # Раскроем содержимое объекта-товара в параметры

                order_cost += price
                # Увеличиваем стоимость заказа

                async with state.proxy() as data:
                    data['products'][idx] = [title, price, count_in_cart]
                    # словарь контекста 'data' по ключу 'products'
                    # и значением будет тоже словарь с ключом 'id' товара
                    # и значением вложенного словаря
                    # будет список с параметрами очередного товара
                    # название, цена, количество товара в корзине

                markup = product_markup(idx, count_in_cart)
                # Берем наш обработчик для формирования
                # разметки карточки товара в корзине

                text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price}₽.'
                # товар, описание, цена

                await message.answer_photo(photo=image,
                                           caption=text,
                                           reply_markup=markup)
                # Выводим ответ-карточку

        if order_cost != 0:  # если общая стоимость не ноль
            # (в корзине есть товары)

            markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                         selective=True)
            markup.add('📦 Оформить заказ')

            await message.answer('Перейти к оформлению?',
                                 reply_markup=markup)
            # Перейти к формированию заказа
            # можно будет только в том, случае если
            # стоимость товаров в корзине не равна нулю
            # (корзина не пуста)


# 4.5 реализуем обработчик добавления товара в корзину (у4-с13)
# -> handlers/user/catalog.py


# 4.6 реализуем обработчик изменения содержимого корзины (у4-с15)
# Листинг 4.11. step_3 /handlers/user/cart.py
@dp.callback_query_handler(IsUser(), product_cb.filter(action='count'))  # окно с количеством товара
@dp.callback_query_handler(IsUser(), product_cb.filter(action='increase'))  # увеличение и
@dp.callback_query_handler(IsUser(), product_cb.filter(action='decrease'))  # и уменьшение количества товара
async def product_callback_handler(query: CallbackQuery, callback_data:
dict,
                                   state: FSMContext):
    '''action='count', action='increase', action='decrease' :
    обработчик будет запускаться при увеличении
     или изменении количества товаров'''

    idx = callback_data['id']  # id товара из словаря с callback данными
    action = callback_data['action']  # действие выполняемое нами, получаем по ключу из словаря
    # Из словаря контекста получаем идентификатор товара и тип действия

    if 'count' == action:
        # при действии (нажатие кнопки) 'count' смотрим количество товаров в заказе

        async with state.proxy() as data:

            if 'products' not in data.keys():
                await process_cart(query.message, state)
            #  если корзина пуста,- будет запущена функция process_cart()
            # сообщение о пустой корзине

            else:
                await query.answer('Количество - ' + data['products'][idx][2])
            #  В противном случае увидим
            #  количество товара count_in_cart = data['products'][idx][2]
            #  ( data['products'][idx] = [title, price, count_in_cart] )

    else:  # action='increase' или action='decrease'

        async with state.proxy() as data:
            if 'products' not in data.keys():
                await process_cart(query.message, state)
                #  если корзина пуста,- будет запущена функция process_cart()
                # сообщение о пустой корзине

            else:
                data['products'][idx][2] += 1 if 'increase' == action else -1
                # Если же товары в корзине присутствуют, мы или увеличим ('increase'),
                # или уменьшим ('decrease') количество конкретного товара

                count_in_cart = data['products'][idx][2]
                # обозначаем новое количество торара в заказе

                if count_in_cart == 0:  # товара больше нет
                    db.query('''DELETE FROM cart 
                    WHERE cid = ? AND idx = ?''', (query.message.chat.id, idx))
                    # Если количество товара равно нулю,
                    # товар из корзины можно удалить

                    await query.message.delete()

                else:
                    db.query('''UPDATE cart 
                    SET quantity = ?
                    WHERE cid = ? AND idx = ?''',
                             (count_in_cart, query.message.chat.id, idx))

                    await query.message.edit_reply_markup(product_markup(idx, count_in_cart))
                # Иначе мы изменим количество товара в базе данных
                # и эти изменения отразим в разметке корзины


# Урок 5. РЕАЛИЗУЕМ РАБОТУ с ЗАКАЗОМ НА СТОРОНЕ КЛИЕНТА

# Обработчик перехода к оформлению заказа (у5-с3)
# Листинг 5.1. /states/checkout_state.py
# Листинг 5.2. /states/__init__.py

# Листинг 5.3. /handlers/user/cart.py
@dp.message_handler(IsUser(), text='📦 Оформить заказ')
async def process_checkout(message: Message, state: FSMContext):
    '''кнопка text='Оформить заказ'
    уже есть в обработчике def process_cart()
    - строка 85'''

    await CheckoutState.check_cart.set()
    #     from states import CheckoutState
    #     Устанавливаем состояние проверки заказа

    await checkout(message, state)


#     Запускаем соответствующий обработчик


# 5.2 реализуем функцию проверки содержимого заказа (у5-с4)

# Листинг 5.4. step_5 /handlers/user/cart.py
# from keyboards.default.markups import * -> разметка check_markup()
async def checkout(message, state):
    answer = ''
    total_price = 0
    # общая стоимость заказа

    async with state.proxy() as data:
        for title, price, count_in_cart in data['products'].values():
            # Опираясь на объект-состояние
            # получаем содержимое словаря-контекста

            # строка 62 -> data['products'][idx] = [title, price, count_in_cart]

            # Из словаря контекста получаем параметры:
            # название, цену товара, количество товара
            # в корзине

            tp = count_in_cart * price
            # Вычисляем стоимость товара в корзине

            answer += f'<b>{title}</b> * {count_in_cart}шт. = {tp}₽\n'
            # Формируем ответ пользователю

            total_price += tp
            # Увеличиваем общую стоимость заказа

    await message.answer(f'{answer}\nОбщая сумма заказа: {total_price}₽.',
                         reply_markup=check_markup())


#     Отправляем ответ пользователю


# Листинг 5.5. step_5 /handlers/user/cart.py
# обработчик, если мы отправим боту некорректное сообщение
@dp.message_handler(IsUser(), lambda message: message.text not in [all_right_message,
                                                                   back_message],
                    state=CheckoutState.check_cart)
async def process_check_cart_invalid(message: Message):
    ''':message.text not in: если ввели что-то
    что не совпадает с кнопками
    :state=: запуск обраб-чика
    при вкл состоянии "проверка корзины" '''

    await message.reply('Такого варианта не было.')


# 5.3 реализуем обраб-к возврата к форм-ю заказа после отображ-я заказ
# (у5-с6)

# Листинг 5.6. step_5 /handlers/user/cart.py
@dp.message_handler(IsUser(), text=back_message,
                    state=CheckoutState.check_cart)
async def process_check_cart_back(message: Message,
                                  state: FSMContext):
    '''
    :text=: нажатие кнопки 'Назад'
    :state=: запуск обраб-чика
    при вкл состоянии "проверка корзины" '''

    await state.finish()  # выкл состояния "проверка корзины"
    await process_cart(message, state)
    # переход к обраб-чику вывода содержимого корзины


# 5.4 реализуем обработчик перехода к вводу имени заказчика
# (у5-с7)
# Листинг 5.7. /handlers/user/cart.py
@dp.message_handler(IsUser(), text=all_right_message,
                    state=CheckoutState.check_cart)
async def process_check_cart_all_right(message: Message,
                                       state: FSMContext):
    '''
        :text=: нажатие кнопки 'Все верно'
        :state=: запуск обраб-чика
        при вкл состоянии "проверка корзины" '''

    await CheckoutState.next()  # name = State()
    # переход к предложению ввода имени заказчика

    await message.answer('Укажите свое имя.',
                         reply_markup=back_markup())
    # запрос имени
    # разметка для возврата к вводу названия


# 5.5 реализуем обработчик возврата к
# формированию заказа после перехода к вводу имени
# (у5-с8)
# Листинг 5.8. step_5 /handlers/user/cart.py
@dp.message_handler(IsUser(), text=back_message, state=CheckoutState.name)
async def process_name_back(message: Message, state: FSMContext):
    '''
        :text=: нажатие кнопки 'Назад'
        :state=: запуск обраб-чика
        при вкл состоянии "ввод имени" '''

    await CheckoutState.check_cart.set()
    # вкл состояния "проверка корзины"

    await checkout(message, state)


#     ф-я проверки содержимого заказа


# 5.6 реализуем обраб-к завершения ввода имени и перехода к адресу
# (у5-с8)
# Листинг 5.9. /handlers/user/cart.py
@dp.message_handler(IsUser(), state=CheckoutState.name)
async def process_name(message: Message, state: FSMContext):
    ''' :state=: запуск обраб-чика
         при вкл состоянии "ввод имени"
         когда вводим имя'''

    async with state.proxy() as data:
        data['name'] = message.text
        # в словарь контекста добавляем имя заказчика по ключу 'name'

        if 'address' in data.keys():

            await confirm(message)
            await CheckoutState.confirm.state()  # confirm = State()
            # Если адрес уже указан,
            # запрашиваем подтверждение правильности оформления заказа
            # ф-я confirm
            # и включаем состояние подтверждения (confirm)

        else:
            await CheckoutState.next()  # address = State()
            await message.answer('Укажите свой адрес места жительства.',
                                 reply_markup=back_markup())
            # Если адрес еще не указан,
            # предлагаем пользователю его указать
            # и переключаемся на состояние address


# 5.7 реализуем обработчик возврата к вводу имени
# (у5-с9)
# Листинг 5.10. step_5 /handlers/user/cart.py
@dp.message_handler(IsUser(), text=back_message,
                    state=CheckoutState.address)
async def process_address_back(message: Message, state: FSMContext):
    '''
        :text=: нажатие кнопки 'Назад'
        :state=: запуск обраб-чика
        при вкл состоянии "ввод адресса" '''
    async with state.proxy() as data:
        await message.answer('Изменить имя с <b>' + data['name'] + '</b>?', reply_markup=back_markup())
        # берем имя из контекста и запрашиваем изменение
        # data['name'] = message.text (строка 306)

    await CheckoutState.name.set()  # переходим в режим ввода имени


# 5.8 реализуем обраб-к завершения ввода адреса и подтверждения заказа
# (у5-с9)
# Листинг 5.11. step_5 /handlers/user/cart.py
@dp.message_handler(IsUser(), state=CheckoutState.address)
async def process_address(message: Message, state: FSMContext):
    ''' :state=: запуск обраб-чика
             при вкл состоянии "ввод адреса"
             когда вводим адрес'''

    async with state.proxy() as data:
        data['address'] = message.text
        # в словарь контекста добавляем адрес заказчика по ключу 'address'

    await confirm(message)
    await CheckoutState.next()
    # запрашиваем подтверждение правильности оформления заказа
    # ф-я confirm
    # и включаем состояние подтверждения (confirm)


# Листинг 5.12. step_5 /handlers/user/cart.py
# (у5-с10)
# ф-я подтверждения правильности оформления заказа
async def confirm(message):
    await message.answer('Убедитесь, что все правильно оформлено и подтвердите заказ.',
                         reply_markup=confirm_markup())
    # confirm_markup() - ф-я формирования разметки
    # для подтверждения заказа


# ф-я формирования разметки для подтверждения заказа
# confirm_markup()
# (у5-с10)
# Листинг 13. /keyboards/default/markups.py


# 5.9 обраб-к ситуации, когда при подтверждении заказа мы вводим текст
# (у5-с10)
# Листинг 5.14. /handlers/user/cart.py
@dp.message_handler(IsUser(),
                    lambda message: message.text not in [confirm_message,
                                                         back_message],
                    state=CheckoutState.confirm)
async def process_confirm_invalid(message: Message):
    ''':message.text not in: если ввели что-то
        что не совпадает с кнопками
        :state=: запуск обраб-чика
        при вкл состоянии "подтверждения заказа" '''

    await message.reply('Такого варианта не было.')


# 5.10 обработчик возврата к изменению адреса
# (у5-с11)
# Листинг 5.15. /handlers/user/cart.py
@dp.message_handler(IsUser(), text=back_message,
                    state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    '''
        :text=: нажатие кнопки 'Назад'
        :state=: запуск обраб-чика
        при вкл состоянии "подтверждения заказа" '''

    await CheckoutState.address.set()
    # переключаемся на состояние ввода адреса

    async with state.proxy() as data:
        await message.answer('Изменить адрес с <b>' + data['address'] +
                             '</b>?',
                             reply_markup=back_markup())
        # # берем адрес из контекста и запрашиваем измененить с текущего
        # Листинг 11. /handlers/user/cart.py -> data['address'] = message.text
        # /keyboards/default/markups.py -> back_markup()


# 5.11 реализуем обработчик завершения формирования заказа
# (у5-с12)
# Листинг 5.16. /handlers/user/cart.py
@dp.message_handler(IsUser(), text=confirm_message,
                    state=CheckoutState.confirm)
async def process_confirm(message: Message, state: FSMContext):

    markup = ReplyKeyboardRemove()
    # без разметки

    logging.info('Deal was made.')

    async with state.proxy() as data:
        cid = message.chat.id
        # id текущего пользователя работающего в боте

        # массив из строк
        products = [idx + '=' + str(quantity)
                    for idx, quantity in db.fetchall('''SELECT idx, 
                    quantity FROM cart WHERE cid=?''', (cid,))]
        # запрос к таблице с корзиной товаров,
        # формируем массив товаров,
        # где каждый товар представлен строкой
        # формата: 'a9cef291062dba543eb97fe5887928f0=1'
        # Справа идентификатор товара, а слева – его количество

        # Далее эти строки в массиве мы будем сцеплять,
        # тем самым формируя общий набор товаров в заказе

        db.query('INSERT INTO orders VALUES (?, ? ,? ,?)',
                 (cid, data['name'], data['address'], ' '.join(products)))
        # Добавляем в таблицу с заказами новую запись
        # с набором заказов пользователя

        db.query('DELETE FROM cart WHERE cid=?', (cid,))
        # Удаляем запись из корзины

        await message.answer('Ok! Ваш заказ уже в пути 🚀\nИмя: <b>' + data[
            'name'] + '</b>\nАдрес: <b>' + data['address'] + '</b> ', reply_markup=markup)
        # Отправляем ответ пользователю

        await state.finish()  # выкл состояния


# 5.12 реализуем отображение активных заказов
# (у5-с13)
# Листинг 17. /handlers/user/delivery_status.py


