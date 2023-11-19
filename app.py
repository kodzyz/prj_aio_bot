from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import ReplyKeyboardRemove
# объект, обеспечивающий старт нашего бота в реальном времени
from aiogram import executor
from logging import basicConfig, INFO

from data.config import ADMINS
from loader import dp, db, bot

# Листинг 3.5. step_2 /app.py
import handlers

# работа нашего бота в реальном времени
# запускаемый модуль проекта

user_message = 'Пользователь'
admin_message = 'Админ'


# Листинг 2.4. step_2 /app.py
# Создаем и регистрируем асинхронный обработчик команды «start» запуска бота
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    '''
    декоратор dp.message_handler - подключаем обработчик к
    системе диспетчеризации проекта(dp)

    commands=['start'] - указывает что
    команда /start будет обрабатываться обработчиком cmd_start

    :param message: объект запроса - сообщение,
    которое пользователь передает боту
    :return:
    '''

    # объект-клавиатура - графический интерфейс
    # resize_keyboard - авто подгонка под размер окна Telegram
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    # две кнопки – для включения админского и пользовательского режимов
    # текст, указан в соответствующей переменной
    markup.row(user_message, admin_message)
    # к каждой кнопке будет обработчик

    # обязательный оператор await в async def -> cmd_start приостанавливается
    # пока не завершится message.answer, вызов которой идет после await
    # при этом приложение может выполнять другие задачи

    await message.answer('''Привет! 👋
    
🤖 Я бот-магазин по подаже товаров любой категории.
    
🛍️ Чтобы перейти в каталог и выбрать приглянувшиеся 
товары возпользуйтесь командой /menu.

❓ Возникли вопросы? Не проблема! Команда /sos поможет 
связаться с админами, которые постараются как можно быстрее откликнуться.
''', reply_markup=markup)


# reply_markup=markup - размещаем две кнопки

# Листинг 2.5. step_2 /app.py
# обработчик к кнопке admin_message - режима администратора
@dp.message_handler(text=admin_message)
async def admin_mode(message: types.Message):
    # нажатие на admin_message делает текущего пользователя Админом

    # получаем id пользователя (id чата)
    cid = message.chat.id

    # добавляем клиента как админа
    if cid not in ADMINS:
        ADMINS.append(cid)

    # На поступивший запрос(нажатие кнопки) мы даем пользователю ответ
    await message.answer('Включен админский режим.',
                         reply_markup=ReplyKeyboardRemove())
    # ReplyKeyboardRemove() - удаляем клавиатуру выбора режима


# Листинг 2.6. step_2 /app.py
# обработчик к кнопке user_message - пользовательский режим
@dp.message_handler(text=user_message)
async def user_mode(message: types.Message):
    cid = message.chat.id
    if cid in ADMINS:
        # удаляем id из списка - клиент не админ, а пользователь
        ADMINS.remove(cid)
    await message.answer('Включен пользовательский режим.',
                         reply_markup=ReplyKeyboardRemove())


# Листинг 2.11. step_2 /app.py
async def on_startup(dp):
    # логирование
    basicConfig(level=INFO)
    # создаем файл базы данных и все необходимые таблицы
    db.create_tables()


if __name__ == '__main__':
    # запуск бота с передачей объекта-диспетчера и функции on_startup()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
# skip_updates=False - если бот выключен,
# ранние входящие сообщения из очереди будут доставлены
