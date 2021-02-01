import sqlite3
from db import db

#Класс-модель айтема
class ItemModel(db.Model):
    #Таблица БД, ассоциируемая с этим классом объектов
    __tablename__ = 'items'

    # Указываем, какие столбцы есть в данной ассоциируемой таблице
    id = db.Column(db.Integer, primary_key=True)  # ID будет главным целочисленным ключом
    name = db.Column(db.String(80))               #name будет строкой не больше 80-ти символов
    price = db.Column(db.Float(precision=2))      #price будет действительным числом с округлением до двух знаков

    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))  #foreing key, привязка к таблице магазинов
    store = db.relationship('StoreModel')  #привязка отношения к модели магазина

    #-------------------------------------

    #Конструктор
    def __init__(self, name, price, store_id):
        # Перечисленные выше столбцы и поля класса ниже должны совпадать + можно вводить допполнительные поля
        self.name = name
        self.price = price
        self.store_id = store_id


    #Функция возврата айтема в JSON-формате
    def json(self):
        return {'id': self.id,
                'name': self.name ,
                'price': self.price,
                'store_id': self.store_id
               }


    # Метод поиска айтема по имени
    @classmethod
    def find_by_name(cls, name):
        #Вернём результат запроса, построенного "строителем запросов" (.query). filter_by - запрос отбора по параметру
        return cls.query.filter_by(name = name).first()  # SELECT * FROM items WHERE name=name LIMIT 1


    # Метод поиска всех айтемов в базе
    @classmethod
    def find_all(cls):
        return cls.query.all()


    # Метод вставки айтема в таблицу БД (работает как insert и как update)
    def save_to_db(self):
        db.session.add(self)  #говорим объекту, добавить себя в БД (значения своих полей)
        db.session.commit()   #сохраняем изменения в БД


    # Метод удаления данных из БД
    def delete_from_db(self):
        db.session.delete(self)  #Говорим БД удалить из таблицы строку с данными этого объекта
        db.session.commit()  #сохраняем изменения