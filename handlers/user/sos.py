from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, Message

from keyboards.default.markups import (all_right_message, cancel_message,
                                       submit_markup)
from states import SosState
from filters import IsUser
from loader import dp, db


# Урок 6. Реализуем подсистему вопросов
# Работа с вопросами на стороне клиента

# предыдущее:
# Листинг 1. step_6 /states/sos_state.py
# Листинг 2. step_6 /states/__init__.py


# 6.1 реализуем обработчик реакции бота
# на вопрос пользователя
# (у6-с3)
# Листинг 6.3. step_6 /handlers/user/sos.py
@dp.message_handler(commands='sos')
async def cmd_sos(message: Message):
    ''':commands=: запуск обр-чка
    при команде 'sos' '''

    await SosState.question.set()
    # Устанавливаем состояние,
    # что бот ожидает получение вопроса
    # от пользователя т.е.
    # переход к вводу вопроса пользователем

    await message.answer('В чем суть проблемы? Опишите как можно детальнее '
                         'и администратор обязательно вам ответит.',
                         reply_markup=ReplyKeyboardRemove())


# подключим маршрутизацию
# обработчиков к проекту:
# Листинг 4. step_6 /handlers/user/__init__.py


# Листинг 5. step_6 /keyboards/default/markups.py
# ф-я для формирования разметки клавиатуры
# подтверждение вопроса пользователя


# 6.2 обработчик подтверждения,
# что вопрос введен верно
# Листинг 6.6. step_6 /handlers/user/sos.py
@dp.message_handler(state=SosState.question)
async def process_question(message: Message, state: FSMContext):
    ''':state=: при вкл состоянии
    question'''

    async with state.proxy() as data:
        data['question'] = message.text
    # Словарь контекста дополняем текстом вопроса
    # где ключ 'question'
    # значение сам текст

    await message.answer('Убедитесь, что все верно.',
                         reply_markup=submit_markup())
    # ф-я для формирования разметки клавиатуры
    # подтверждение вопроса пользователя
    # Листинг 5. step_6 /keyboards/default/markups.py

    await SosState.next()  # submit = State()
    # Переключаемся на следующее состояние,
    # переход к шагу
    # подтверждения вопроса пользователем


# 6.3 реализуем обработчик ввода
# пользователем текста вместо подтвержд
# Листинг 6.7. step_6 /handlers/user/sos.py
@dp.message_handler(lambda message: message.text not in [cancel_message,
                                                         all_right_message],
                    state=SosState.submit)
async def process_price_invalid(message: Message):
    await message.answer('Такого варианта не было.')


# 6.4 реализуем обработчик отмены вопроса от пользователя
# (у6-с6)
# Листинг 6.8. step_6 /handlers/user/sos.py
@dp.message_handler(text=cancel_message, state=SosState.submit)
async def process_cancel(message: Message, state: FSMContext):
    await message.answer('Отменено!', reply_markup=ReplyKeyboardRemove())
    await state.finish()  # выкл текущее состояние


# 6.5 реализуем обработчик отправки запроса
# Листинг 6.8. step_6 /handlers/user/sos.py
@dp.message_handler(text=all_right_message, state=SosState.submit)
async def process_submit(message: Message, state: FSMContext):
    '''кнопка: all_right_message
    состояние: 'подтверждения' '''

    cid = message.chat.id
    # id текущего клиента

    if db.fetchone('SELECT * FROM questions WHERE cid=?', (cid,)) is None:
        # Проверяем, что у пользователя нет активных вопросов

        async with state.proxy() as data:
            db.query('INSERT INTO questions VALUES (?, ?)',
                     (cid, data['question']))
        # Опираясь на дополненный ранее словарь контекста
        # Листинг 6. step_6 /handlers/user/sos.py
        # получаем содержимое заданного вопроса
        # и добавляем его в базу данных

        await message.answer('Отправлено!',
                             reply_markup=ReplyKeyboardRemove())
        # Отмечаем факт отправки запроса пользователем
    else:
        await message.answer(
            'Превышен лимит на количество задаваемых вопросов.',
            reply_markup=ReplyKeyboardRemove())
        # Если у пользователя уже есть активные вопросы,
        # сообщаем о превышении лимита
        # заданных вопросов

    await state.finish()  # выкл текущее состояние

# далее:
# РЕАЛИЗУЕМ РАБОТУ с ВОПРОСАМИ НА СТОРОНЕ АДМИНА
# Листинг 6.9. step_6 /handlers/questions.py
