#ИМПОРТЫ
from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister
from resources.item import Item, ItemList
from resources.store import Store, StoreList  #если не импортировать Store, использующий StoreModel, то SQLA не создаст таблицу для магазинов в БД

from db import db

import os

#----------------------------------------------------
#НАЧАЛЬНЫЕ БАЗОВЫЕ НАСТРОЙКИ API

app = Flask(__name__)  # инициализируем приложение Flask

#НАСТРОЙКИ SQLAlchemy ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db') #после запятой - запасной вариант на локальной локации  #Указываем SQLA, где искать файл БД
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False       #OFFаем отслеживание изменений и оставляем базовый трэкинг от Flask

#ОБЪЯВЛЯЕМ СЕКРЕТНЫЙ КЛЮЧ
app.secret_key = 'jose' #Секретный ключ, который никто не должен знать

#ПРИВЯЗЫВАЕМ API К ПРИЛОЖЕНИЮ Flask
api = Api(app)  #создаём интерфейс и связываем его с приложением

#--------------------------------------------------------

#SQLA создаст файл и все таблицы при включении приложения
@app.before_first_request
def create_tables():
    db.create_all()

#--------------------------------------------------------

#ОБЪЯВЛЯЕМ РАБОТЫ СИСТЕМЫ АУТЕНТИФИКАЦИИ ПО JWT-ТОКЕНАМ
jwt = JWT(app, authenticate, identity)  #создаём объект системы JWT   # /auth

#---------------------------------------------------

#Добавляем созданный класс айтема в качестве ресурса (имя класса, путь обращения)
api.add_resource(Item, '/item/<string:name>')  # к примеру http://127.0.0.1:5000/student/Rolf

#Добавляем созданный класс списка айтемов в качестве ресурса (имя класса, путь обращения)
api.add_resource(ItemList, '/items')

#Добавляем созданный класс регистратора пользователей в качестве ресурса
api.add_resource(UserRegister, '/register')

#Добавляем созданный класс магазина
api.add_resource(Store, '/store/<string:name>')

#Добавялем класс списка магазинов в качестве ресурса
api.add_resource(StoreList, '/stores')

#---------------------------------------------------

#ЗАПУСК API
if __name__ == '__main__':
    db.init_app(app)                    #(SQLA) инициализируем БД с приложением
    app.run(port = 5000, debug = True)  #Запускаем приложение