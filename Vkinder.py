import datetime
import time
from random import randrange

import requests
import vk_api
from tqdm import tqdm
from vk_api.longpoll import VkEventType, VkLongPoll

from config import comm_token, user_token
from database import *
from keyboard import keyboard1, keyboard2
from method import Data

dictionary = {}


def profile_loading_counter(user_id):
    user_id = int(user_id)
    if user_id in dictionary:
        dictionary[user_id] += 20
    else:
        dictionary[user_id] = 20
    return dictionary[user_id]


def reset_profile_loading_counter(user_id):
    try:
        user_id = int(user_id)
        dictionary.pop(user_id)
    except KeyError:
        pass


class VKBotSearch:
    def __init__(self):
        print('Бот запущен')
        self.vk = vk_api.VkApi(token=comm_token)
        self.longpoll = VkLongPoll(self.vk)
        self.data = Data()

    def loop_bot(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                message_text = event.text
                return message_text, event.user_id

    def write_msg(self, user_id, message, keyboard=None, attachment=None):
        self.vk.method('messages.send', {'user_id': user_id,
                                         'message': message,
                                         'random_id': randrange(10 ** 7),
                                         'attachment': attachment,
                                         'keyboard': keyboard
                                         })

    def name(self, user_id):
        #Извлечение имени пользователя
        first_name = self.data.get_user_info(user_id)['first_name']
        return first_name

    def get_sex(self, user_id):
        #Извлечение пола пользователя для автоматического подбора
        sex = self.data.get_user_info(user_id)['sex']
        if sex == 2:
            sex = 1
        elif sex == 1:
            sex = 2
        else:
            sex = None
        return sex

    def get_sex_individual_parameters(self, user_id):
        #Извлечение пола для поиска по индивидуальным предпочтениям
        sex_dict = {'мужской': 2, 'женский': 1}
        self.write_msg(user_id, 'Введите пол для поиска (мужской/женский): ')
        while True:
            msg_text, user_id = self.loop_bot()
            if msg_text in sex_dict:
                return sex_dict[msg_text]
            else:
                self.write_msg(user_id, 'Ошибка ввода. Попробуйте ещё раз.')
                return self.get_sex_individual_parameters(user_id)

    def get_age(self, user_id):
        #Извлечение возраста для авто подбора
        bdate = self.data.get_user_info(user_id)['bdate'].split('.')
        if len(bdate) == 3:
            age = int(datetime.date.today().year) - int(bdate[2])
            age_from = str(age - 1)
            age_to = str(age + 1)
        elif len(bdate) == 2:
            age_from = self.get_age_low(user_id)
            age_to = self.get_age_high(user_id)
        else:
            return None
        return age_from, age_to

    def get_age_low(self, user_id):
        #Извлечение возраста по минимальной границе по индивидуальным предпочтениям
        self.write_msg(user_id, 'Введите минимальный искомый возраст (min - 18): ')
        msg_text, user_id = self.loop_bot()
        age_from = int(msg_text)
        if age_from < 18:
            self.write_msg(user_id, 'Ошибка ввода. Введите возраст не менее 18ти лет.')
            return self.get_age_low(user_id)
        else:
            return age_from

    def get_age_high(self, user_id):
        #Извлечение возраста по максимальной границе по индивидуальным предпочтениям
        self.write_msg(user_id, 'Введите максимальный искомый возраст (max - 99): ')
        msg_text, user_id = self.loop_bot()
        age_to = int(msg_text)
        if age_to > 99:
            self.write_msg(user_id, 'Ошибка ввода. Введите возраст не более 99ти лет.')
            return self.get_age_high(user_id)
        else:
            return age_to

    def find_city(self, user_id):
        #Извлечение информации о городе
        if 'city' not in self.data.get_user_info(user_id):
            return self.find_city_individual_parameters(user_id)
        else:
            hometown = self.data.get_user_info(user_id)['city']['title']
            return hometown

    def find_city_individual_parameters(self, user_id):
        #Извлечение информации о городе по индивидуальным предпочтениям
        self.write_msg(user_id, 'Введите название города в котором следует искать: ')
        msg_text, user_id = self.loop_bot()
        hometown = str(msg_text)
        cities = self.data.get_cities(user_id)
        for city in cities:
            if city['title'] == hometown.title():
                self.write_msg(user_id, f'Ищу в городе {hometown.title()}')
                return hometown.title()
        self.write_msg(user_id, 'Ошибка ввода')
        result = self.find_city_individual_parameters(user_id)
        if result is None:
            return None
        else:
            return result

    def find_user_params(self, user_id):
        #Сбор параметров для авто поиска
        fields = 'id, sex, bdate, city, relation'
        age_from, age_to = self.get_age(user_id)
        params = {'access_token': user_token,
                  'v': '5.131',
                  'sex': self.get_sex(user_id),
                  'age_from': age_from,
                  'age_to': age_to,
                  'country_id': '1',
                  'hometown': self.find_city(user_id),
                  'fields': fields,
                  'status': '1' or '6',
                  'count': profile_loading_counter(user_id),
                  'has_photo': '1',
                  'is_closed': False
                  }
        return params

    def find_user_individual_parameters(self, user_id):
        #Сбор параметров для поиска по идвивидуальным предпочтениям
        fields = 'id, sex, bdate, city, relation'
        params = {'access_token': user_token,
                  'v': '5.131',
                  'sex': self.get_sex_individual_parameters(user_id),
                  'age_from': self.get_age_low(user_id),
                  'age_to': self.get_age_high(user_id),
                  'country_id': '1',
                  'hometown': self.find_city_individual_parameters(user_id),
                  'fields': fields,
                  'status': '1' or '6',
                  'count': profile_loading_counter(user_id),
                  'has_photo': '1',
                  'is_closed': False
                  }
        return params

    def search_users(self, user_id):
        #Поиск юзеров по полученным данным для авто поиска
        method = 'users.search'
        all_persons = []
        url = f'https://api.vk.com/method/{method}'
        res = requests.get(url, self.find_user_params(user_id)).json()
        user_url = f'https://vk.com/id'
        count = res['response']['count']  #считаем сколько найдено анкет
        count_list = []  #считаем сколько анкет с открытым профилем и с хотя бы одной фотографией
        for element in tqdm(res['response'].get('items'), desc="Loading: ", ncols=100, colour='green'):

            profile_pics = self.data.get_photos_id(element['id'])
            if profile_pics:
                attach = ''
                for pic in profile_pics['pics_ids']:
                    attach += f'photo{profile_pics["owner_id"]}_{pic},'
                person = [
                    element['first_name'],
                    element['last_name'],
                    user_url + str(element['id']),
                    element['id'],
                    attach
                ]
                all_persons.append(person)
                count_list = len(all_persons)
        print(
            f'Поиск закончен, всего найдено {count} юзеров. Для просмотра загружаю {count_list} пользователей')
        if count == 0:
            self.write_msg(user_id, f"К сожалению нет подходящих вариантов")
            print('Нет подходящих вариантов')
        else:
            self.write_msg(user_id,
                           f'Нашел для Вас несколько вариантов, проверяю есть ли фотографии и открыт ли профиль...')
        return all_persons

    def search_users_individual_parameters(self, user_id):
        #Поиск юзеров по полученным данным для поиска по индивидуальным предпочтениям
        method = 'users.search'
        all_persons = []
        url = f'https://api.vk.com/method/{method}'
        res = requests.get(url, self.find_user_individual_parameters(user_id)).json()
        user_url = f'https://vk.com/id'
        count = res['response']['count']  #считаем сколько анкет найдено
        count_list = []  #считаем сколько анкет с открытым профилем и с хотя бы одной фотографией
        for element in tqdm(res['response'].get('items'), desc="Loading: ", ncols=100, colour='green'):
            profile_pics = self.data.get_photos_id(element['id'])
            if profile_pics:
                attach = ''
                for pic in profile_pics['pics_ids']:
                    attach += f'photo{profile_pics["owner_id"]}_{pic},'
                person = [
                    element['first_name'],
                    element['last_name'],
                    user_url + str(element['id']),
                    element['id'],
                    attach
                ]
                all_persons.append(person)
                count_list = int(len(all_persons))
        print(
            f'Поиск закончен, всего найдено {count} юзеров. Для просмотра загружаю {count_list} пользователей')
        if count == 0:
            self.write_msg(user_id, f"К сожалению нет подходящих вариантов")
            print('Нет подходящих вариантов')
        else:
            self.write_msg(user_id,
                           f'Нашел для Вас несколько вариантов, проверяю есть ли фотографии и открыт ли профиль...')
        return all_persons

    def sorted_users(self, user_id):
        #Возврат списка юзеров отсортированных по критериям
        profiles = self.search_users(user_id)
        profiles_to_send = []
        seen_profiles = set()
        while len(profiles) > 0:
            profile = profiles.pop()
            if profile[3] not in seen_profiles:
                if select(user_id, profile[3]) is None:  #проверяем нет ли повторений
                    profiles_to_send.append(profile)
                seen_profiles.add(profile[3])
        return profiles_to_send

    def send_info_about_users(self, user_id):
        #Отправка информации о найденых профилях
        profiles_to_send = self.sorted_users(user_id)
        if not profiles_to_send:
            self.write_msg(user_id, f'Все анкеты просмотрены')
        else:
            while len(profiles_to_send) > 0:
                profile = profiles_to_send.pop()
                insert_data_seen_users(user_id, profile[3])
                self.write_msg(user_id, f'\n{profile[0]}  {profile[1]}  {profile[2]}', attachment={profile[4]})
                self.write_msg(user_id, f'Если юзер Вам не подходит, то нажимайте "Еще варианты!"',
                               keyboard1.get_keyboard())
                self.write_msg(user_id,
                               f'Чтобы начать новый поиск, а также посмотреть другие возможности, нажмите "Закончить просмотр"',
                               keyboard2.get_keyboard())
                msg_text, user_id = self.loop_bot()
                if msg_text == 'Еще варианты':
                    continue
                else:
                    self.write_msg(user_id, f'Жду других команд.')
                    break
            else:
                self.send_info_about_users(user_id)

    def sorted_users_individual_parameters(self, user_id):
        #Возврат списка юзеров отсортированных по критериям индивидуальных предпочтений
        profiles = self.search_users_individual_parameters(user_id)
        profiles_to_send = []
        seen_profiles = set()
        while len(profiles) > 0:
            profile = profiles.pop()
            if profile[3] not in seen_profiles:
                if select(user_id, profile[3]) is None:
                    profiles_to_send.append(profile)
                seen_profiles.add(profile[3])
        return profiles_to_send

    def send_info_about_users_individual_parameters(self, user_id):
        #Отправка информации о найденых профилях по индивидуальным предпочтениям
        profiles_to_send = self.sorted_users_individual_parameters(user_id)
        if not profiles_to_send:
            self.write_msg(user_id, f'Все анкеты просмотрены')
        else:
            while len(profiles_to_send) > 0:
                profile = profiles_to_send.pop()
                insert_data_seen_users(user_id, profile[3])
                self.write_msg(user_id, f'\n{profile[0]}  {profile[1]}  {profile[2]}', attachment={profile[4]})
                self.write_msg(user_id, f'Если юзер Вам не подходит, то нажимайте "Еще варианты!"',
                               keyboard1.get_keyboard())
                self.write_msg(user_id,
                               f'Чтобы начать новый поиск, а также посмотреть другие возможности, нажмите "Закончить просмотр"',
                               keyboard2.get_keyboard())
                msg_text, user_id = self.loop_bot()
                if msg_text == 'Еще варианты':
                    continue
                else:
                    self.write_msg(user_id, f'Жду других команд.')
                    break
            else:
                self.send_info_about_users_individual_parameters(user_id)

bot = VKBotSearch()