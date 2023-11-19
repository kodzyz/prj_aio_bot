# класс-менеджер для работы с базой данных
# взаимодействие с бд - DB-API
# https://habr.com/ru/articles/321510/
# СУБД - SQLite

from sqlite3 import connect


# Листинг 2.2 step_2 /utils/db/storage.py
class DatabaseManager:
    '''класс-менеджер для работы
    с базой данных'''

    def __init__(self, path):
        # Создаем соединение с базой данных
        self.conn = connect(path)

        # запрос на включение поддержки внешних ключей
        self.conn.execute('pragma foreign_keys = on')
        # настройки фиксируются
        self.conn.commit()
        # Создаем объект-курсор
        # Через него выполняются все операции с базой данных
        self.cur = self.conn.cursor()

    def create_tables(self):
        '''создание таблиц'''
        self.query(
            'CREATE TABLE IF NOT EXISTS products (idx text, title text,'
            ' body text, photo blob, price int, tag text)')
        self.query(
            'CREATE TABLE IF NOT EXISTS orders (cid int, usr_name text,'
            ' usr_address text, products text)')
        self.query(
            'CREATE TABLE IF NOT EXISTS cart (cid int, idx text,'
            ' quantity int)')  # id, id товара и количество
        self.query(
            'CREATE TABLE IF NOT EXISTS categories (idx text, title text)')
        # self.query(
        #     'CREATE TABLE IF NOT EXISTS wallet (cid int, balance real)')
        self.query(
            'CREATE TABLE IF NOT EXISTS questions (cid int, question text)')

    def query(self, arg, values=None):
        '''выполнить любой SQL-запрос'''
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        self.conn.commit()

    def fetchone(self, arg, values=None):
        '''запрос к базе данных на получение одной записи'''
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        # Получаем результат сделанного запроса
        return self.cur.fetchone()

    def fetchall(self, arg, values=None):
        '''запрос к базе данных на получение списка записей'''
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        # Получаем результат сделанного запроса
        return self.cur.fetchall()

    def __del__(self):
        '''закрытие СУБД'''
        self.conn.close()
