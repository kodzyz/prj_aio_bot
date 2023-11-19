from aiogram.dispatcher.filters.state import StatesGroup, State


# РЕАЛИЗУЕМ РАБОТУ с ЗАКАЗОМ НА СТОРОНЕ КЛИЕНТА

# 5.1 реализуем обработчик перехода к формированию заказа
# При работе с заказом у нас также будут фигурировать состояния,
# т.е. параметры заказа, при установке которых
# будут запускаться определенные обработчики


# Листинг 5.1. step_5 /states/checkout_state.py
class CheckoutState(StatesGroup):
    check_cart = State()
    name = State()
    address = State()
    confirm = State()

# Настроим импорты класса
# Листинг 5.2. /states/__init__.py

# Обработчик перехода к оформлению заказа
# Листинг 5.3. /handlers/user/cart.py
