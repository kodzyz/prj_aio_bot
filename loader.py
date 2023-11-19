# выражения, отвечающие за
# создание объекта бота и некоторые базовые настройки

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from utils.db.storage import DatabaseManager
from data import config

# Листинг 2.3. step_2 /loader.py

# создаем объект бота
# ParseMode.HTML - режим форматирования сообщений с HTML-разметкой
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

# бэкенд для хранения состояний между этапами взаимодействия с ботом
# хранилище MemoryStorage позволяет хранить все данные в оперативной памяти
storage = MemoryStorage()

# диспетчеризация запросов - подход, применяемый в Django и Flask
# объект диспетчера для обработки входящих сообщений и запросов
dp = Dispatcher(bot, storage=storage)

# объект менеджера баз данных - относительный путь
db = DatabaseManager('data/database.db')
