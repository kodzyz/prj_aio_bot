from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.types.chat import ChatActions

from handlers.user.menu import questions  # '❓ Вопросы'
from keyboards.default.markups import all_right_message, cancel_message, submit_markup
from loader import dp, db, bot
from filters import IsAdmin
from states import AnswerState

# Формируем шаблон с возвращаемыми данными
# cid: id клиента,- кому слать ответ
question_cb = CallbackData('question', 'cid', 'action')


# предыдущее:
# Работа с вопросами на стороне клиента
# step_6 /handlers/user/sos.py

# РЕАЛИЗУЕМ РАБОТУ с ВОПРОСАМИ НА СТОРОНЕ АДМИНА
# 6.6 реализуем обработчик отображения списка вопросов
# (урок 6-стр.8)
# Листинг 6.9. step_6 /handlers/admin/questions.py
@dp.message_handler(IsAdmin(), text=questions)
async def process_questions(message: Message):
    ''':text=: нажатие кнопки
    '❓ Вопросы' '''

    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    # Имитируем набор сообщения человеком

    questions = db.fetchall('SELECT * FROM questions')
    # список вопросов(список кортежей) из бд

    if len(questions) == 0:  # Если вопросов нет

        await message.answer('Нет вопросов.')

    else:

        for cid, question in questions:
            markup = InlineKeyboardMarkup()
            # для каждого вопроса формируем кнопку
            # и добавляем в разметку
            markup.add(InlineKeyboardButton(
                'Ответить',
                callback_data=question_cb.new(cid=cid, action='answer')))
            # cid=: id пользователя,- кому слать ответ
            # action=: к каждой кнопке привязываем обработчик
            # при нажатии будет передаваться id пользователя

            await message.answer(question, reply_markup=markup)
            # увидим текст вопроса(question) и
            # разметку с кнопкой 'Ответить'


# подключим обработчики к системе маршрутизации проекта
# Листинг 10. step_6 /handlers/admin/__init__.py


# класс с состояниями
# Листинг 11. step_6 /states/questions.py

# 6.7 реализуем обработчик, обеспечивающий переход к вводу ответа
# (у6-с10)
# Листинг 6.13. step_6 /handlers/admin/questions.py
# from states import AnswerState
@dp.callback_query_handler(IsAdmin(), question_cb.filter(action='answer'))
async def process_answer(query: CallbackQuery, callback_data: dict,
                         state: FSMContext):
    ''':text=: нажатие кнопки
        'Ответить' '''

    async with state.proxy() as data:
        data['cid'] = callback_data['cid']
        # Пополняем словарь контекста id пользователя

        # id получаем из «коллбека» с данными
        # Листинг 9. step_6 /handlers/questions.py
        # callback_data=question_cb.new(cid=cid, action='answer')))

    await query.message.answer('Напиши ответ.',
                               reply_markup=ReplyKeyboardRemove())
    # Предлагаем админу ввести ответ на вопрос пользовтаеля

    await AnswerState.answer.set()
    # Устанавливаем состояние ожидания ответа на вопрос


# 6.8 реализуем обработчик подтверждения правильности ответа
# (у6-с11)
# Листинг 6.14. step_6 /handlers/admin/questions.py
@dp.message_handler(IsAdmin(), state=AnswerState.answer)
async def process_submit(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['answer'] = message.text
    # Пополняем словарь контекста
    # текстом сообщения – ответом на вопрос

    await AnswerState.next()  # submit = State()
    # Переключаемся в состояние
    # подтверждения ответа

    await message.answer('Убедитесь, что не ошиблись в ответе.',
                         reply_markup=submit_markup())
    # submit_markup - (cancel_message, all_right_message)


# 6.9 реализуем обработчик отмены ответа
# (у6-с12)
# Листинг 6.15. step_6 /handlers/admin/questions.py
@dp.message_handler(IsAdmin(), text=cancel_message,
                    state=AnswerState.submit)
async def process_send_answer(message: Message, state: FSMContext):
    await message.answer('Отменено!', reply_markup=ReplyKeyboardRemove())
    await state.finish()
    # Выключаем состояние -
    # откат к исходному положению


# 6.10 реализуем обработчик отправки ответа пользователю
# (у6-с13)
# Листинг 6.16. step_6 /handlers/admin/questions.py
@dp.message_handler(IsAdmin(), text=all_right_message,
                    state=AnswerState.submit)
async def process_send_answer(message: Message, state: FSMContext):
    # Получаем из контекста ответ пользователя и его id
    async with state.proxy() as data:
        answer = data['answer']
        # Листинг 14. step_6 /handlers/admin/questions.py

        cid = data['cid']
        # Листинг 13. step_6 /handlers/admin/questions.py

        question = db.fetchone(
            'SELECT question FROM questions WHERE cid=?', (cid,))[0]
        # Получаем текст вопроса пользователя

        db.query('DELETE FROM questions WHERE cid=?', (cid,))
        # Удаляем вопрос пользователя

        text = f'Вопрос: <b>{question}</b>\n\nОтвет: <b>{answer}</b>'
        # Формируем текст вопроса и ответа

        await message.answer('Отправлено!',
                             reply_markup=ReplyKeyboardRemove())
        # Извещаем админа об отправке ответа

        await bot.send_message(cid, text)
        # Отправляем через объект бота
        # ответ автору вопроса

    await state.finish()
    # Выключаем состояние
