# состояния - объекты которые можно вкл/выкл тем самым настроить
# запуск тех или иных обработчиков

from aiogram.dispatcher.filters.state import StatesGroup, State


# Листинг 3.6. step_3 /states/product_state.py
class CategoryState(StatesGroup):
    '''Создаем класс-группу объектов состояний для категорий товаров'''
    # как только состояние будет меняться
    # (мы ввели название категории),
    # будет запускаться соответствующий обработчик
    title = State()


# Листинг 3.13. step_3 /states/product_state.py
class ProductState(StatesGroup):
    '''шаблон класса для состояний товара'''
    # Состояния у нас будут на указание всех основных параметров,
    # а также кнопки сохранения информации о товаре
    title = State()
    body = State()
    image = State()
    price = State()

    # кнопка подтверждения сохранения данных по всем товарам
    confirm = State()
