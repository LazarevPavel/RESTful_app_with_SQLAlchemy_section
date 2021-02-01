#ИМПОРТЫ
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh
from resources.item import Item, ItemList
from resources.store import Store, StoreList  #если не импортировать Store, использующий StoreModel, то SQLA не создаст таблицу для магазинов в БД
from blacklist import BLACKLIST

from db import db

import os

#----------------------------------------------------
#НАЧАЛЬНЫЕ БАЗОВЫЕ НАСТРОЙКИ API

app = Flask(__name__)  # инициализируем приложение Flask

#НАСТРОЙКИ SQLAlchemy ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db') #после запятой - запасной вариант на локальной локации  #Указываем SQLA, где искать файл БД
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False       #OFFаем отслеживание изменений и оставляем базовый трэкинг от Flask
app.config['PROPAGATE_EXCEPTIONS'] = True   #API будет возвращать кастомные ошибки (вместо 500), которые при возникновении будут передоваться из Фласк-расширений (например JWT)
app.config['JWT_BLACKLIST_ENABLED'] = True #включение директивы на отсеивание юзеров состоящих в чёрном списке
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']  #директива на проверку токена при попытках получения доступа или обновлении токена

#ОБЪЯВЛЯЕМ СЕКРЕТНЫЙ КЛЮЧ
app.secret_key = 'jose' #Секретный ключ, который никто не должен знать   #app.config['JWT_SECRET_KEY']

#ПРИВЯЗЫВАЕМ API К ПРИЛОЖЕНИЮ Flask
api = Api(app)  #создаём интерфейс и связываем его с приложением

#--------------------------------------------------------

#SQLA создаст файл и все таблицы при включении приложения
@app.before_first_request
def create_tables():
    db.create_all()

#--------------------------------------------------------

#ОБЪЯВЛЯЕМ РАБОТЫ СИСТЕМЫ АУТЕНТИФИКАЦИИ ПО JWT-ТОКЕНАМ
jwt = JWTManager(app)  #создаём объект системы JWTManager  #не создаёт /auth точку входа


#Дополнительные возможности системы токенов, которые позволяют сопоставлять токены с любыми данными
@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:   #если айди юзера равен 1 (забито вручную, надо менять на подсос данных из БД)
        return {'is_admin': True}  #то он Админ
    return {'is_admin': False}  #иначе не админ


#Действия на случай попытки подключения юзера, находящегося в чёрном списке
@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    #return decrypted_token['identity'] in BLACKLIST  #возвращаем правду или ложь в зависимости от того, состоит ли юзер (проверяем по ID юзера) в чёрном списке
    return decrypted_token['jti'] in BLACKLIST  #возвращаем правду или ложь в зависимости от того, состоит ли токен (проверяем по ID токена) в чёрном списке (список деактивирвоанных)


#Действия при истечении срока использования токена юзером
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
                    'description': 'The token has expired.',
                    'error': 'token_expire'
    }), 401


#Действия, когда пользователь прислал неправильный токен
@jwt.invalid_token_loader
def invalid_token_callback():
    return jsonify({
        'description': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


#Действия при попытке юзером сделать что-то без требуемой авторизации
@jwt.unauthorized_loader
def missing_token_callback():
    return jsonify({
        'description': 'Request does not contain an access token.',
        'error': 'authorization_required'
    }), 401


#Требование свежего токена от пользователя
@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        'description': 'The token is not fresh.',
        'error': 'fresh_token_required'
    })


#Деактивация работающего токена пользователя
@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    }), 401


#---------------------------------------------------

#Добавляем созданный класс айтема в качестве ресурса (имя класса, путь обращения)
api.add_resource(Item, '/item/<string:name>')  # к примеру http://127.0.0.1:5000/student/Rolf

#Добавляем созданный класс списка айтемов в качестве ресурса (имя класса, путь обращения)
api.add_resource(ItemList, '/items')

#Добавляем созданный класс регистратора пользователей в качестве ресурса
api.add_resource(UserRegister, '/register')

#Добавляем созданный класс логина пользователей в качестве ресурса
api.add_resource(UserLogin, '/login')

#Добавляем созданный класс разлогина пользователей в качестве ресурса
api.add_resource(UserLogout, '/logout')

#Добавляем созданный класс пользователя в качестве ресурса
api.add_resource(User, '/user/<int:user_id>')

#Добавляем созданный класс магазина
api.add_resource(Store, '/store/<string:name>')

#Добавялем класс списка магазинов в качестве ресурса
api.add_resource(StoreList, '/stores')

#Добавляем класс ТокенРефрешера в качестве ресурса
api.add_resource(TokenRefresh, '/refresh')
#---------------------------------------------------

#ЗАПУСК API
if __name__ == '__main__':
    db.init_app(app)                    #(SQLA) инициализируем БД с приложением
    app.run(port = 5000, debug = True)  #Запускаем приложение