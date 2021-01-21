import sqlite3
from db import db


#Класс-модель пользователя
class UserModel(db.Model):
    __tablename__ = 'users'  #мы указываем SQLAlchemy, с какой таблицей ассоциируется этот класс объектов

    #Указываем, какие столбцы есть в данной ассоциируемой таблице
    id = db.Column(db.Integer, primary_key=True)  #ID будет главным целочисленным ключом
    username = db.Column(db.String(80))           #username будет строкой не больше 80ти символов
    password = db.Column(db.String(80))           #password так же

    #-----------------------------------------

    #Конструктор класса
    def __init__(self, username, password):
        #Перечисленные выше столбцы и поля класса ниже должны совпадать + можно вводить допполнительные поля
        self.username = username
        self.password = password

    #--------------------------------------

    # Поиск пользователя по имени
    @classmethod
    def find_by_username(cls, username):
        # Вернём результат запроса, построенного "строителем запросов" (.query). filter_by - запрос отбора по параметру
        return cls.query.filter_by(username=username).first()  # SELECT * FROM users WHERE username=username LIMIT 1

    #------------------------------------------------------

    # Поиск пользователя по ID
    @classmethod
    def find_by_id(cls, _id):
        # Вернём результат запроса, построенного "строителем запросов" (.query). filter_by - запрос отбора по параметру
        return cls.query.filter_by(id=_id).first()  # SELECT * FROM users WHERE id=_id LIMIT 1

    #----------------------------------------------------

    #Сохранение юзера в БД
    def save_to_db(self):
        db.session.add(self) #просим SQLA добавить юзера в БД
        db.session.commit()  #сохраняем изменения в БД