from filters import IsUser
from aiogram.types import Message, CallbackQuery
from aiogram.types.chat import ChatActions

from keyboards.inline.categories import categories_markup, category_cb
from keyboards.inline.products_from_catalog import product_markup, product_cb
from .menu import catalog  # кнопка Каталог
from loader import dp, db, bot


# При нажатии на кнопку Каталог,
# будет запускаться следующий обработчик,
# который предлагает пользователю выбрать категорию для показа товара (у4-с5)
# Листинг 4.2. step_4 /handlers/user/catalog.py
@dp.message_handler(IsUser(), text=catalog)
async def process_catalog(message: Message):
    '''обработчик перехода к указанию категории'''

    await message.answer('Выберите раздел, чтобы вывести список товаров:',
                         reply_markup=categories_markup())
    # categories_markup() -> вывод списка категорий


# обработчик перехода к выводу всех товаров категории (у4-с6)
# но ещё не сам вывод
# Листинг 4.4. step_4 /handlers/user/catalog.py
@dp.callback_query_handler(IsUser(), category_cb.filter(action='view'))
async def category_callback_handler(query: CallbackQuery, callback_data: dict):
    products = db.fetchall('''SELECT * FROM products product
    WHERE product.tag = (SELECT title FROM categories WHERE idx=?)
     AND product.idx NOT IN (SELECT idx FROM cart WHERE cid = ?)''',
                           (callback_data['id'], query.message.chat.id))
    # запрос к базе данных и получаем список товаров по id категории
    # и обязательно чтобы товара не было в списке выбранных товаров (в корзине)
    # в словаре callback_data с возвращаемыми данными есть и id категории
    # (from keyboards.inline.categories import category_cb)

    await query.answer('Все доступные товары.')
    # эта надпись появляется в табличке и исчезает

    await show_products(query.message, products)
    # список кнопок, где каждая кнопка соответствует отдельному товару (у4-с6)
    # products - на вход принимает массив товаров


# keyboards.inline.products_from_catalog.py -> визуализация карточки товара у юзера (у4-с6)


# функция отображения списка товаров (у4-с7)
# Листинг 4.6. step_4 /handlers/user/catalog.py
async def show_products(m, products):
    if len(products) == 0:
        await m.answer('Здесь ничего нет 😢')
        # Если товаров в каталоге нет

    else:
        await bot.send_chat_action(m.chat.id, ChatActions.TYPING)
        # Включаем имитацию печати человеком

        for idx, title, body, image, price, _ in products:
            # Для каждого товара получаем id категории, название товара, описание, фото, цену

            markup = product_markup(idx, price)
            # для каждого товара делаем разметку - функция product_markup
            # (кнопка с указанием цены и добавлением товара в корзину)

            text = f'<b>{title}</b>\n\n{body}'
            # текст с названием и описанием товара

            await m.answer_photo(photo=image, caption=text, reply_markup=markup)
            # Выводим карточку товара с фото, названием, описанием и разметкой -
            # где будет цена и кнопкой добавления в корзину


# 4.5 реализуем обработчик добавления товара в корзину (у4-с13)
# Листинг 4.10. step_4 /handlers/user/catalog.py
@dp.callback_query_handler(IsUser(), product_cb.filter(action='add'))
async def add_product_callback_handler(query: CallbackQuery, callback_data: dict):
    # добавление записи в таблицу с корзиной товаров
    db.query('INSERT INTO cart VALUES (?, ?, 1)', (query.message.chat.id, callback_data['id']))
    # query.message.chat.id - текущий id пользователя
    # callback_data['id'] - id товара

    await query.answer('Товар добавлен в корзину!')
    await query.message.delete()


# 4.6 реализуем обработчик изменения содержимого корзины (у4-с15)
# -> handlers/user/cart.py
