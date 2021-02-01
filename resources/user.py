#Импорты
import sqlite3
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (create_access_token,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_jwt_identity,
                                get_raw_jwt)

from models.user import UserModel
from blacklist import BLACKLIST

#-------------------------------------------------------------------------

_user_parser = reqparse.RequestParser()  # Создаём общий для всех классов парсер запроса

_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help='This field can not be left blank'
                          )  # добавляем указание, какой аргумент парсить из запроса

_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help='This field can not be left blank'
                          ) # добавляем указание, какой аргумент парсить из запроса

#---------------------------------------------------------------

#Класс регистратора пользователей (наследован от Ресурса)
class UserRegister(Resource):

    #Когда на вход поступают данные для регистрации
    def post(self):
        data = _user_parser.parse_args()  # Парсим запрос и забираем оттуда данные

        #Если такой пользователь уже существует
        if UserModel.find_by_username(data['username']):
            return {"message": "A user with that username already exists."}, 400

        user = UserModel(data['username'], data['password'])  #создаём юзермодель с данными пользователя
        user.save_to_db()   #заносим пользователя в БД через созданную юзермодель

        return {"message": "User created successfully."} , 201


#Класс пользователя
class User(Resource):
    #метод получения пользователя по ID
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not User:
            return {'message': 'User not found'}, 404
        return user.json(), 200


    #Метод удаления пользователя по ID
    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not User:
            return {'message': 'User not found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200


#Класс логинизации пользователя
class UserLogin(Resource):

    @classmethod
    def post(cls):
        data = _user_parser.parse_args()  #берём данные из запроса
        user = UserModel.find_by_username(data['username'])  #ищем указанного пользователя в БД

        #функция "authenticate()" перкочевала сюда
        #Если пароли совпадают
        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)  #создаёт токен доступа | identity= это то, что делает функция "identity()"
            refresh_token = create_refresh_token(user.id)  #создаёт обновляемый токен
            return {'access_token': access_token, 'refresh_token': refresh_token} , 200  #и возвращаем оба токена

        return {'message': 'Invalid credentials'}, 401 #если пароли не совпали, возвращаем ошибку


#Класс разлогинизации пользователя
class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']   #jti - это специальный ID токена
        BLACKLIST.add(jti)           #добавляем этот айдишник в блэклист
        return {'message': 'Successfully logged out.'}, 200   #возвращаем ответочку


#Класс для обновления токенов пользователей
class TokenRefresh(Resource):
    @jwt_refresh_token_required     #декоратор, требуеющий обновления токена юзера
    def post(self):
        current_user = get_jwt_identity()  #получить юзера в соответствии с токеном
        new_token = create_access_token(identity=current_user, fresh=False)  #генерация нового non-fresh токена для указанного пользователя
        return {'access_token': new_token}, 200    #возвращаем новый токен