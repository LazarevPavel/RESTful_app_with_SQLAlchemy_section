#ИМПОРТЫ
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from models.store import StoreModel

#-------------------------------------------------

#Класс магазина, наследованный от класса Ресурса (ресурсы - это все данные, с которыми оперирует API),
class Store(Resource):

    #Получить магазин по имени
    @jwt_required
    def get(self, name):
        store = StoreModel.find_by_name(name) #ищем магазин
        if store:
            return store.json()  #если нашли - возвращаем данные магазина
        return {'message': 'Store not found'}, 404  #иначе выбрасываем ошибку


    #Добавить новый магазин или обновить старый
    @jwt_required
    def post(self, name):
        #Если такой магазин уже существует
        if StoreModel.find_by_name(name):
            return {'message': 'A store with name "{}" already exists'.format(name)}, 400   #выкинем ошибку

        store = StoreModel(name) #создаём объект магазина
        try:
            store.save_to_db()  #сохраняем
        except:
            return {'message': 'An error occured while creating the store.'}, 500  #чёт пошло не так - выкинем ошибку

        #если всё ок, возвращаем магазин в формате JSON
        return store.json(), 201


    #Удалить магазин по имени
    @jwt_required
    def delete(self, name):
        store = StoreModel.find_by_name(name) #ищем магазин по имени
        if store:
            store.delete_from_db()  #удаляем магазин

        return {'message': 'Store deleted'}, 200  #выкидываем сообщение об успешном операции

#----------------------------------------------------

#Класс списка магазинов, наследованный от класса Ресурса
class StoreList(Resource):

    #Получить список магазинов
    @jwt_required
    def get(self):
        return {'stores': [store.json() for store in StoreModel.find_all()]}

#------------------------------------------------------

