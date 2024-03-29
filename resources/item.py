#ИМПОРТЫ
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, fresh_jwt_required, jwt_optional, get_jwt_claims, get_jwt_identity
from models.item import ItemModel


#Класс айтем, наследованный от класса Ресурса (ресурсы - это все данные, с которыми оперирует API),
class Item(Resource):
    #Общий объект для всего класса айтема
    parser = reqparse.RequestParser()  # Создаём парсер запроса
    parser.add_argument('price', type=float, required=True, help='This field can not be left blank')  # добавляем указание, какой аргумент парсить из запроса
    parser.add_argument('store_id', type=int, required=True, help='Every item needs a store id')  # добавляем указание, какой аргумент парсить из запроса

    #Метод получения айтема по имени
    @jwt_required     #проверка на авторизованность
    def get(self, name):
        item = ItemModel.find_by_name(name) #Ищем в базе файл по имени

        #Если айтем нашёлся
        if item:
            return item.json(), 200 #возвращаем айтем
        #иначе возвращаем ошибку
        return {'message': 'Item not found'}, 404


    #Метод создания нового айтема
    @fresh_jwt_required
    def post(self, name):
        #Пробегаемся по списку айтемов, и если айтем с таким именем уже существует
        if ItemModel.find_by_name(name):
            return {'message': 'An item with name "{}" already exists.'.format(name)}, 400  #выбрасываем сообщение об ошибке

        #Если такого айтема ещё нет в списке, то добавляем его
        data = Item.parser.parse_args()  # Парсим запрос и забираем оттуда данные

        item_model = ItemModel(name, data['price'], data['store_id']) #создаём описание айтема

        #Пробуем вставить элемент в базу
        try:
            item_model.save_to_db()
        except: #в случае непредвиденной ошибки
            return {"message": "An error occured inserting the item."}, 500  #Internal server error

        return item_model.json(), 201                #возвращаем созданный айтем и код http протокола, означающий, что айтем создан


    #Удаление айтема из списка
    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()  #берём данные из токена

        if not claims['is_admin']:  #если запрос пришёл от НЕ юзера-админа
            return {'message': 'Admin privilege required.'}, 401  #выдаём ошибку

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {'message': 'Item deleted'}


    #Добавление или обновление айтема
    @jwt_required
    def put(self, name):
        data = Item.parser.parse_args()      #Парсим запрос и забираем оттуда данные

        item = ItemModel.find_by_name(name)  #ищем новый айтем по данным пользователя

        if item is None:        #Если айтема нет в базе
            item = ItemModel(name, data['price'], data['store_id']) #создаём айтем
        else:    #Если такой айтем уже есть
            item.price = data['price']  #меняем характеристику "цена" найденного объекта айтема

        item.save_to_db()  #сохраняем найденный и изменённый (или созданный) объект айтема в БД
        return item.json(), 200 #возвращаем JSON представление айтема

#---------------------------------------------------

#Класс списка айтемов, наследованный от класса Ресурс
class ItemList(Resource):
    #Получить список всех айтемов
    @jwt_optional  #декоратор опционального возврата на запрос identity. То есть JWTManager сможет вернуть None, если юзер на авторизован
    def get(self):
        #Даёт ID юзера (но в силу jwt_optional может дать и None - это значит, что юзер не залогинился)
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]  #выгружаем полный набор айтемов

        if user_id:  #если юзер был авторизован
            return {'items': items}, 200   #возвращаем полный набор всех характеристик айтемов

        #Иначе выгружаем только названия айтемов
        return {'items': [item['name'] for item in items],
                'message': 'More data available if you log in.'
               }, 200
#---------------------------------------------------