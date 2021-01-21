#Импорты
import sqlite3
from flask_restful import Resource, reqparse
from models.user import UserModel


#Класс регистратора пользователей (наследован от Ресурса)
class UserRegister(Resource):
    # Общий объект для всего класса айтема
    parser = reqparse.RequestParser()  # Создаём парсер запроса
    parser.add_argument('username', type=str, required=True, help='This field can not be left blank')  # добавляем указание, какой аргумент парсить из запроса
    parser.add_argument('password', type=str, required=True, help='This field can not be left blank')


    #Когда на вход поступают данные для регистрации
    def post(self):
        data = UserRegister.parser.parse_args()  # Парсим запрос и забираем оттуда данные

        #Если такой пользователь уже существует
        if UserModel.find_by_username(data['username']):
            return {"message": "A user with that username already exists."}, 400

        user = UserModel(data['username'], data['password'])  #создаём юзермодель с данными пользователя
        user.save_to_db()   #заносим пользователя в БД через созданную юзермодель

        return {"message": "User created successfully."} , 201