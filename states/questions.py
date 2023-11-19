from aiogram.dispatcher.filters.state import StatesGroup, State


# предыдущее:
# РЕАЛИЗУЕМ РАБОТУ с ВОПРОСАМИ НА СТОРОНЕ АДМИНА
# Листинг 9. step_6 /handlers/questions.py
# Листинг 10. step_6 /handlers/admin/__init__.py

# класс с состояниями
# Листинг 6.11. step_6 /states/questions.py
class AnswerState(StatesGroup):
    answer = State()  # состояние ожидания ответа на вопрос
    submit = State()  # состояние - подтверждение отправки вопроса

# настроим импорт нового класса с состояними
# Листинг 12. step_6 /states/__init__.py
