import sqlite3
from db import db

#Класс-модель айтема
class StoreModel(db.Model):
    #Таблица БД, ассоциируемая с этим классов объектов
    __tablename__ = 'stores'

    # Указываем, какие столбцы есть в данной ассоциируемой таблице
    id = db.Column(db.Integer, primary_key=True)  # ID будет главным целочисленным ключом
    name = db.Column(db.String(80))               #name будет строкой не больше 80-ти символов

    items = db.relationship('ItemModel', lazy='dynamic')  #привязка отношений с айтем моделью

    #-------------------------------------

    #Конструктор
    def __init__(self, name):
        # Перечисленные выше столбцы и поля класса ниже должны совпадать + можно вводить допполнительные поля
        self.name = name


    #Функция возврата магазина в JSON-формате
    def json(self):
        return {'id': self.id,
                'name': self.name,
                'items': [item.json() for item in self.items.all()]
               }


    # Метод поиска магазина по имени
    @classmethod
    def find_by_name(cls, name):
        #Вернём результат запроса, построенного "строителем запросов" (.query). filter_by - запрос отбора по параметру
        return cls.query.filter_by(name = name).first()  # SELECT * FROM stores WHERE name=name LIMIT 1


    #Метод поиска всех магазинов в базе
    @classmethod
    def find_all(cls):
        cls.query.all()


    # Метод вставки магазина в таблицу БД (работает как insert и как update)
    def save_to_db(self):
        db.session.add(self)  #говорим объекту, добавить себя в БД (значения своих полей)
        db.session.commit()   #сохраняем изменения в БД


    # Метод удаления данных из БД
    def delete_from_db(self):
        db.session.delete(self)  #Говорим БД удалить из таблицы строку с данными этого объекта
        db.session.commit()  #сохраняем изменения