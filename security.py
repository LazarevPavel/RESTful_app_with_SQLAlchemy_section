#Ипортируем класс пользователя
from models.user import UserModel
from werkzeug.security import safe_str_cmp


#Функция аутентификации
def authenticate(username, password):
    user = UserModel.find_by_username(username)   #Получаем через БД данные пользователя по имени (или None, если такого нет)
    if user and safe_str_cmp(user.password, password):        #Если пароль этого пользователя правильный
        return user                               #возвращаем данные пользователя


#Назначение ID (токена JWT) пользователю
def identity(payload):
    user_id = payload['identity']      #Берём ID из аргумента
    return UserModel.find_by_id(user_id)    #Возвращаем данные пользвателя из БД по id
