from aiogram.dispatcher.filters.state import StatesGroup, State


# Урок 6. Реализуем подсистему вопросов

# Работа с вопросами на стороне клиента

# класс с состояниями
# (у6-с3)
# Листинг 6.1. step_6 /states/sos_state.py
class SosState(StatesGroup):
    question = State()  # состояние - задать вопрос
    submit = State()  # состояние - подтверждение отправки вопроса

# настроим импорт
# Листинг 2. step_6 /states/__init__.py
