# Подключим обработчики администратора к проекту
# тем самым мы импортируем дополненный админскими обработчиками
# объект маршрутизатора

# Листинг 3.2. step_2 /handlers/admin/__init__.py
from .add import dp

# Листинг 5.22. step_5 /handlers/admin/__init__.py
from .orders import dp

# Листинг 6.10. step_6 /handlers/admin/__init__.py
from .questions import dp
