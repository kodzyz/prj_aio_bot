# Урок 2. Создаем начальную конфигурацию проекта

# Урок 2.1 СОЗДАЕМ НАЧАЛЬНУЮ СТРУКТУРУ ПРОЕКТА

# Добавим в корень проекта запускаемый модуль app.py.

# перейдем к созданию еще одного служебного файла – loader.py

# в корне мы создадим директорию utils для модулей
# со вспомогательными блоками кода
# Добавим в нее вложенную директорию db,
# а уже в нее модуль storage.py

# добавим в корень проекта директорию data,
# а в нее модуль config.py

# Добавим в корень директорию filters
# для модулей, обеспечивающих
# возможность переключения
# между режимами админа и пользователя

# Урок 2.2 СОЗДАЕМ НАСТРОЙКИ ПРОЕКТА
# Заполним модуль config.py первыми выражениями
# Листинг 2.1. step_2 data/config.py

# Урок 2.3 СОЗДАЕМ НАСТРОЙКИ БАЗЫ ДАННЫХ
# Листинг 2.2 step_2 /utils/db/storage.py

# Урок 2.4 НАСТРАИВАЕМ МОДУЛЬ LOADER
# Листинг 2.3. step_2 /loader.py

# Урок 2.5 НАСТРАИВАЕМ МОДУЛЬ APP
# Листинг 2.4. step_2 /app.py
# Листинг 2.5. step_2 /app.py
# Листинг 2.6. step_2 /app.py

# Урок 2.6 СОЗДАЕМ ОБРАБОТЧИКИ ПЕРЕХОДА В МЕНЮ
# (начальные настройки обработчиков)
# Добавим в корень проекта директорию handlers,
# в нее вложенные директории admin и user,
# а в директорию user модуль menu.py

# Урок 2.7 создаем фильтры
# в директории filters создадим следующую структуру
# __init__.py
# is_admin.py
# is_user.py
# Листинг 2.7. step_2 /filters/is_user.py
# Листинг 2.8. step_2 /filters/is_admin.py
# Листинг 2.9. step_2 /filters/__init__.py

# Урок 2.8 добавляем обработчики вывода меню для каждого из режимов
# Листинг 2.10. step_2 /handlers/user/menu.py

# Урок 2.9 ПРОВЕРЯЕМ РАБОТУ ПРОЕКТА
# Листинг 2.11. step_2 /app.py
