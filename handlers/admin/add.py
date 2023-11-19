# режим администратора -> меню =
# необходимо реализовать логику для всех трех блоков интерфейса администратора:
# Настройка каталога, Вопросы, Заказы

# обработчик настройка каталога = вывод всех категорий товаров
# блок с категориями и кнопкой добавления категории


from aiogram.types import (Message, InlineKeyboardMarkup,
                           InlineKeyboardButton, CallbackQuery,
                           ReplyKeyboardMarkup, ReplyKeyboardRemove)

# коллбэк - объекты, создаваемые для кнопок
# и содержащие произвольное число параметров
# при нажатии кнопки коллбек заполняется параметрами
from aiogram.utils.callback_data import CallbackData
from hashlib import md5
from aiogram.dispatcher import FSMContext
from aiogram.types.chat import ChatActions
from aiogram.types import ContentType

from handlers.user.menu import settings  # Настройка каталога
from loader import db, dp, bot
from filters import IsAdmin
# состояния
from states import CategoryState
from states import ProductState
# Листинг 3.34. step_3 /handlers/admin/add.py
from keyboards.default.markups import *

# коллбэк-данные для нашего бота
# category префикс - название коллбэка
# id - идентификатор добавляемой категории
# action - обработчик действия по кнопке
category_cb = CallbackData('category', 'id', 'action')
product_cb = CallbackData('product', 'id', 'action')

# cancel_message = '🚫 Отменить'
add_product = '➕ Добавить товар'
delete_category = '🗑️ Удалить категорию'


# back_message = '👈 Назад'
# all_right_message = '✅ Все верно'

# Листинг 3.1. step_3 /handlers/admin/add.py

# обработчик списка действующих категорий
# IsAdmin() - является ли пользователь админом
# text=settings - кнопка по которой запускается обработчик
@dp.message_handler(IsAdmin(), text=settings)
async def process_settings(message: Message):
    # создание клавиатуры
    markup = InlineKeyboardMarkup()

    # Делаем запрос к базе данных, получаем список категорий
    # Для каждой категории извлекаем id и название категории
    for idx, title in db.fetchall('SELECT * FROM categories'):
        # Для каждой категории создаем кнопку с названием категории
        markup.add(InlineKeyboardButton(
            title, callback_data=category_cb.new(id=idx, action='view')))
        # action='view' - обработчик category_callback_handler
        # значение view у нас будет при нажатии на кнопку с названием категории

    # Возвращаемые данные – это идентификатор категории
    # по нему будем получать список товаров категории
    # и тип действия (action='view') - обозначает,
    # что мы будем просматривать содержимое категории
    # при нажатии на кнопку с названием категории
    # (далее создадим обработчик)

    # Размещаем в клавиатуре кнопку добавления категории
    markup.add(InlineKeyboardButton(
        '+ Добавить категорию', callback_data='add_category'))
    # указатель callback_data='add_category' - далее создадим обработчик
    # он будет запускаться на действие add_category,
    # т.е. при нажатии кнопки добавления категории

    # callback_data это как в Django-шаблонах мы добавляем динамические ссылки

    # Выводим перед пользователем надпись и блок кнопок
    await message.answer('Настройка категорий:', reply_markup=markup)
    # где каждая кнопка соответствует категории
    # плюс одна кнопка для добавления новой категории


# Листинг 3.8. step_3 /handlers/admin/add.py
# логика добавления категории
# обработчик обратного вызова (запроса),
# который мы привязали к кнопке добавления категории (при нажатии)
@dp.callback_query_handler(IsAdmin(), text='add_category')
async def add_category_callback_handler(query: CallbackQuery):
    # Обработчик принимает объект запроса

    await query.message.delete()
    # удаляем предыдущее сообщение в интерфейсе нашего бота

    await query.message.answer('Название категории?')
    # Передаем текст подсказки для ввода названия категории

    await CategoryState.title.set()
    # админ введет название категории, а мы установим состояние
    # вкл. состояние(title) для обработки введенного нового названия категории
    # обработчик set_category_title_handler


# Листинг 3.9. step_3 /handlers/admin/add.py
# при измении состояния state=CategoryState.title(add новой категории) - запускается обработчик
@dp.message_handler(IsAdmin(), state=CategoryState.title)
async def set_category_title_handler(message: Message, state: FSMContext):
    category = message.text
    # получаем введенное админом название новой категории

    idx = md5(category.encode('utf-8')).hexdigest()
    # Идентификатором категории будет ее захешированное название

    db.query('INSERT INTO categories VALUES (?, ?)', (idx, category))
    # запись idx, title в базу данных

    await state.finish()
    # выкл установленное состояние (процесс создания категории)

    await process_settings(message)
    # Обновляем список действующих категорий


# Листинг 3.10. step_3 /handlers/admin/add.py
# логика отображения товаров категории - просматривать содержимое категории
# при нажатии на кнопку с названием категории
# выводился бы список товаров этой категории

# привязка обработчика для коллбека action='view' ф-ции process_settings
@dp.callback_query_handler(IsAdmin(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery,
                                    callback_data: dict,
                                    state: FSMContext):
    category_idx = callback_data['id']
    # из словаря с возвращаемыми данными извлекаем id категории
    # чтобы получить все товары категории

    products = db.fetchall('''SELECT * FROM products product
     WHERE product.tag = (SELECT title FROM categories WHERE idx=?) ''', (category_idx,))
    # запрос на получение всех товаров категории по ее id

    await query.message.delete()
    await query.answer('Все добавленные товары в эту категорию.')
    # Удаляем предыдущее сообщение интерфейса и выводим новое

    await state.update_data(category_index=category_idx)
    # дополнения контеста новым аргументом id категории

    # как получить содержимое контеста по ключу из словаря:
    #     async with state.proxy() as data:
    #         if 'category_index' in data.keys():
    #             idx = data['category_index']

    await show_products(query.message, products, category_idx)
    # вызов ф-ии визуализации всех товаров категории


# Листинг 3.11. step_3 /handlers/admin/add.py
# вывод всех товаров категории
async def show_products(m, products, category_idx):
    '''
    визуализация всех товаров категории
    :param m: объект сообщения
    :param products: список кортежей (TABLE products) где каждый соответствует определенному продукту
    :param category_idx: идентификатор категории
    :return:
    '''
    await bot.send_chat_action(m.chat.id, ChatActions.TYPING)
    # опция печати ботом сообщения, как будто печатает живой человек

    # Далее для каждого товара нам нужно по сути сформировать карточку
    # Распаковываем содержимое кортежа каждого товара в набор параметров
    for idx, title, body, image, price, tag in products:
        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} рублей.'
        # Формируем текст в карточке товара

        markup = InlineKeyboardMarkup()
        # Создаем объект клавиатуры

        # Добавляем в клавиатуру кнопку для удаления товара
        markup.add(InlineKeyboardButton(
            '🗑️ Удалить',
            callback_data=product_cb.new(id=idx, action='delete')))
        # Привязываем к ней соответствующий «коллбек»
        # action='delete' обработчик удаления товара:
        # delete_product_callback_handler

        await m.answer_photo(photo=image,
                             caption=text,
                             reply_markup=markup)
        # Отправляем ответ пользователю, где выводим фото товара и ранее сформированный текст

    markup = ReplyKeyboardMarkup()
    markup.add(add_product)
    markup.add(delete_category)
    # Формируем главное меню бота,
    # в котором размещаем кнопку добавления товара и удаления категории

    await m.answer('Хотите что-нибудь добавить или удалить?', reply_markup=markup)
    # Выводим главное меню с дополнительной подсказкой


# Листинг 3.12. step_3 /handlers/admin/add.py
# реализуем логику удаления категории
@dp.message_handler(IsAdmin(), text=delete_category)
async def delete_category_handler(message: Message, state: FSMContext):
    # метод proxy() -> обратиться к содержимому контекста
    # получить содержимое состояния в виде словаря
    async with state.proxy() as data:
        if 'category_index' in data.keys():  # методы: все ключи
            idx = data['category_index']
            # получаем значение идентификатора по ключу из словаря

            db.query(
                'DELETE FROM products WHERE tag IN (SELECT '
                'title FROM categories WHERE idx=?)', (idx,))
            db.query('DELETE FROM categories WHERE idx=?', (idx,))
            # удаляем объект категории из базы данных
            # сначало товары из категории потом саму категорию

            await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())
            await process_settings(message)
            # Удаляем клавиатуру предыдущего сообщения,
            # отправляем сообщение «Готово»
            # и вновь выводим список категорий


# 3.5 реализуем логику указания названия нового товара (с16)
# Листинг 3.15 step_3 /handlers/admin/__add__.py
@dp.message_handler(IsAdmin(), text=add_product)
async def process_add_product(message: Message):
    await ProductState.title.set()
    # Устанавливаем объект состояния для названия товара
    # для дальнейшей обработки введенного названия

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    # Формируем главное меню бота,
    markup.add(cancel_message)
    # кнопка отмены при нажатии на которую
    # будет запускать обработчик 'process_cancel'
    # отмены добавления нового товара

    await message.answer('Название?', reply_markup=markup)
    # пользователю будет предложено ввести название товара


# 3.6 реализуем логику отмены добавления нового товара (урок3-ст16)
# Листинг 3.16. step_3 /handlers/admin/__add__.py
# чтобы в любой момент завершить добавление товара
# state=ProductState.title -
# обработчик работает при включении состояния для параметра Название категории
@dp.message_handler(IsAdmin(), text=cancel_message, state=ProductState.title)
async def process_cancel(message: Message, state: FSMContext):
    await message.answer('Ок, отменено!', reply_markup=ReplyKeyboardRemove())
    await state.finish()
    # При отмене выводим соответствующее сообщение и выключаем состояние

    await process_settings(message)
    # Переходим обратно к списку категорий товаров


# 3.7 реализуем логику добавления описания товара после ввода названия
# (ур3-с18)
# Листинг 3.17. step_3 /handlers/admin/__add__.py
@dp.message_handler(IsAdmin(), state=ProductState.title)
async def process_title(message: Message, state: FSMContext):
    '''обработчик добавления описания товара после ввода названия'''
    # обработчик будет запускаться после изменения состояния title,
    # т.е. когда мы введем название товара

    async with state.proxy() as data:
        data['title'] = message.text
        # Передаем в словарь контекста название товара

        await ProductState.next()
        await message.answer('Описание?', reply_markup=back_markup())
        # Переходим к следующему состоянию: body = State()
        # где нам будет предложено ввести описание товара

        # reply_markup=back_markup() - функция чтобы
        # при необходимости мы могли вернуться на
        # предыдущий шаг к вводу названия


# функция back_markup перенесена в модуль keyboards

# Листинг 3.18. step_3 /handlers/admin/__add__.py
# def back_markup():
#     '''разметка для возврата к вводу названия'''
#     markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#     # selective=True - выборачная разметка, только для IsAdmin
#
#     markup.add(back_message)
#     # кнопка отмены
#     # обработчик process_title_back
#
#     return markup


# при нажатии кнопки back_message(кнопка отмены)
# происходит повторное создание товара -> process_title_back
# и изменение названия товара -> process_body_back
# Листинг 3.19. step_3 /handlers/admin/__add__.py
@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.title)
async def process_title_back(message: Message, state: FSMContext):
    '''обработчик возврата к добавлению товара,
    который будет отрабатывать только после
    указания названия товара -> строка 205'''
    await process_add_product(message)


# Листинг 3.20. step_3 /handlers/admin/__add__.py
@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.body)
async def process_body_back(message: Message, state: FSMContext):
    '''поменять название товара можно только
     на этапе ввода описания (объект состояния body)'''
    await ProductState.title.set()
    # Устанавливаем объект состояния для названия товара
    # для дальнейшей обработки введенного названия

    async with state.proxy() as data:
        await message.answer(f"Изменить название с <b>{data['title']}</b>?",
                             reply_markup=back_markup())
    # Введем название товара, перейдем к описанию, а затем вернемся обратно


# 3.8 реализуем логику запроса на добавление фото товара (у3-с19)
# Листинг 3.21. step_3 /handlers/admin/__add__.py
@dp.message_handler(IsAdmin(), state=ProductState.body)
async def process_body(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['body'] = message.text
        # дополняем словарь контекста описанием товара

    await ProductState.next()
    # переход к следующему состоянию -> image = State()

    await message.answer('Фото?', reply_markup=back_markup())
    # запрос фото


# 3.9 реализуем логику добавления цены товара (у3-с21)
# Листинг 3.22. step_3 /handlers/admin/__add__.py
# обработчик добавления фото и перехода к указанию цены после добавления фото
@dp.message_handler(IsAdmin(), content_types=ContentType.PHOTO,
                    state=ProductState.image)
async def process_image_photo(message: Message, state: FSMContext):
    # В Telegram есть стандартная опция прикрепления сообщению фото
    fileID = message.photo[-1].file_id
    # получаем id объекта который мы добавили к интерфейсу в Telegram (фото)

    file_info = await bot.get_file(fileID)
    # получаем добавленный файл(объект-фото) по id

    downloaded_file = (await bot.download_file(file_info.file_path)).read()
    # загрузка фото -> получение пути загрузки фото

    async with state.proxy() as data:
        data['image'] = downloaded_file
        # пополняем словарь контекста: привязка объекта к ключу 'image'

    await ProductState.next()
    # следующее состояние -> price = State()

    await message.answer('Цена?', reply_markup=back_markup())
    # выводим сообщение с запросом цены


# 3.10 реализуем логику формирования карточки товара после ввода цены (у3-с22)
# Листинг 3.23. step_3 /handlers/admin/__add__.py
# lambda message: message.text.isdigit() -> валидация,
# цена должна быть целым числом
@dp.message_handler(IsAdmin(), lambda message: message.text.isdigit(),
                    state=ProductState.price)
async def process_price(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text
        # дополним словарь контекста

        title = data['title']
        body = data['body']
        price = data['price']
        # берем из контекста содержимое

        await ProductState.next()
        # confirm = State() -> состояние подтверждение

        text = f'<b>{title}</b>\n\n{body}\n\nЦена: {price} рублей.'

        markup = check_markup()
        # разметка из двух кнопок

        await message.answer_photo(photo=data['image'],
                                   caption=text,
                                   reply_markup=markup)


# функция check_markup перенесена в модуль keyboards
# Листинг 3.24. step_3 /handlers/admin/__add__.py
# def check_markup():
#     markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
#     markup.row(back_message, all_right_message)
#
#     return markup


# 3.11 реализуем итоговый обработчик регистрации товара (у3-с23)
# Листинг 3.25. step_3 /handlers/admin/__add__.py
@dp.message_handler(IsAdmin(), text=all_right_message,
                    state=ProductState.confirm)
async def process_confirm(message: Message, state: FSMContext):
    async with state.proxy() as data:
        title = data['title']
        body = data['body']
        image = data['image']
        price = data['price']
        # по параметрам из словаря контекста сделаем записи в бд

        tag = db.fetchone(
            'SELECT title FROM categories WHERE idx=?',
            (data['category_index'],))[0]
        # название категории товара по ее id

        idx = md5(' '.join([title, body, price, tag]
                           ).encode('utf-8')).hexdigest()
        # формируем и хешируем строку с параметрами товара,
        # чтобы не хранить явно

        db.query('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)',
                 (idx, title, body, image, int(price), tag))
        # вставка в бд

        await state.finish()
        await message.answer('Готово!', reply_markup=ReplyKeyboardRemove())

        await process_settings(message)
        # обновляем список категории с товарами


# 3.12 реализуем логику удаления товара категории (у3-с26)
# Листинг 3.26. step_3 /handlers/admin/__add__.py
@dp.callback_query_handler(IsAdmin(), product_cb.filter(action='delete'))
async def delete_product_callback_handler(query: CallbackQuery,
                                          callback_data: dict):
    '''
    обработчик обратного вызова, который мы привязали
    к кнопке удаления товара в методе show_products()
    теперь любой товар можно удалить
    '''

    product_idx = callback_data['id']
    # id продукта из словаря

    db.query('DELETE FROM products WHERE idx=?', (product_idx,))
    # удаляем продукт из бд

    await query.answer('Удалено!')

    await query.message.delete()
    # убираем сообщение которое выводилось до этого


# 3.13 реализуем логику изменения цены и описания товара (у3-с26)
# Листинг 3.27. step_3 /handlers/admin/__add__.py
# Когда мы указали название, описание, фото, цену -
# мы можем захотеть и вернуться к редактированию цены
@dp.message_handler(IsAdmin(), text=back_message, state=ProductState.confirm)
async def process_confirm_back(message: Message, state: FSMContext):
    '''
    state=ProductState.confirm: Данный обработчик
     срабатывает при состоянии подтверждения добавления товара
    (состояние – confirm)
    '''
    await ProductState.price.set()
    # Включаем состояние изменения цены

    async with state.proxy() as data:
        await message.answer(f"Изменить цену с <b>{data['price']}</b>?",
                             reply_markup=back_markup())
    # мы меняем цену, нам нужно знать текущее ее значение,
    # поэтому обращаемся к словарю контекста
    # за текущим значением цены


# И второй обработчик, когда мы хотим изменить
# описание товара или,
# когда вместо фото, добавили текст (у3-с28)
# Листинг 3.28. step_3 /handlers/admin/__add__.py
@dp.message_handler(IsAdmin(), content_types=ContentType.TEXT,
                    state=ProductState.image)
async def process_image_url(message: Message, state: FSMContext):
    '''
    state=ProductState.image: С указанным обработчиком работаем,
     когда добавляем фото т.е. включено соответствующее состояние
    '''
    if message.text == back_message:
        await ProductState.body.set()
        # Если нажимаем кнопку «Назад»,
        # включаем состояние изменения описания (body)

        async with state.proxy() as data:

            await message.answer(f"Изменить описание с <b>{data['body']}</b>?",
                                 reply_markup=back_markup())
            # Предлагаем подтвердить изменение описания
    else:
        await message.answer('Вам нужно прислать фото товара.')
        # Если вводим вместо фото текст


# 3.14 реализуем логику обработчиков-валидаторов (у3-с29)

# На случай совершения пользователем ошибок
# нужно настроить соответствующие обработчики

# Первый позволит обработать ситуацию указания цены
# в неверном формате, например, строковом
# Листинг 3.29. step_3 /handlers/admin/__add__.py
@dp.message_handler(IsAdmin(), lambda message: not message.text.isdigit(),
                    state=ProductState.price)
async def process_price_invalid(message: Message, state: FSMContext):
    '''
    lambda message: not message.text.isdigit() ->
    обработчик реагирует если цена не число

    state=ProductState.price -> работа с ценой
    '''
    if message.text == back_message:
        await ProductState.image.set()
        async with state.proxy() as data:
            await message.answer("Другое изображение?",
                                 reply_markup=back_markup())
    # возможность возврата к замене фото

    else:
        await message.answer('Укажите цену в виде числа!')


# И еще один обработчик на тот случай,
# если пользователь вместо подтверждения добавления товара
# в конце или отмены добавления напишет какой-то текст
# Листинг 3.30. step_3 /handlers/admin/__add__.py
@dp.message_handler(IsAdmin(), lambda message: message.text not in [back_message,
                                                                    all_right_message],
                    state=ProductState.confirm)
async def process_confirm_invalid(message: Message, state: FSMContext):
    await message.answer('Такого варианта не было.')

# 3.15 реализуем модуль с функциями формирования разметки клавиатуры

# В модуле add.py есть функции back_markup, check_markup
# отвечающие за формирование клавиатуры.
# Они не относятся непосредственно к логике проекта,
# поэтому вынесем их в отдельный модуль.
# Добавим в пакет проекта директорию keyboards,
# в нее вложенную папку default.
# В эту папку поместим два модуля __init__.py и markups.py.
