# обработчик интерфейса пользователя

from aiogram.types import ReplyKeyboardMarkup, Message
# импортируем объект-диспетчер запросов
from loader import dp
from filters import IsUser, IsAdmin

# Листинг 2.10. step_2 /handlers/user/menu.py

# переменные с текстом надписей на кнопках клавиатуры нашего бота
catalog = '🛍️ Каталог'
cart = '🛒 Корзина'
delivery_status = '🚚 Статус заказа'

settings = '⚙️ Настройка каталога'
orders = '🚚 Заказы'
questions = '❓ Вопросы'


# декораторы перехватывата нажатия кнопки меню
# IsUser(), IsAdmin() - добавляем объекты фильтра
# при включении режима админа или юзера,
# запускается указанный далее обработчик

@dp.message_handler(IsAdmin(), commands='menu')
async def admin_menu(message: Message):
    # создаем объект клавиатуры,
    # добавляем три кнопки
    # selective - клавиатура показывается не всем
    # в зависимости от объекта фильтра входящим как админ или юзер
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(settings)
    markup.add(questions, orders)
    # и отправляем ответ пользователю
    await message.answer('Меню', reply_markup=markup)


@dp.message_handler(IsUser(), commands='menu')
async def user_menu(message: Message):
    markup = ReplyKeyboardMarkup(selective=True)
    markup.add(catalog)
    markup.add(cart)
    markup.add(delivery_status)

    await message.answer('Меню', reply_markup=markup)
