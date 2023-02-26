import requests

from config import user_token


class Data:
    def __init__(self):
        self.user_token = user_token

    def get_cities(self, user_id):
        #получения списка городов
        method = 'database.getCities'
        params = {'country_id': 1,
                  'need_all': 0,
                  'count': 1000,
                  'user_id': user_id,
                  'access_token': user_token,
                  'v': '5.131',
                  }
        url = f'https://api.vk.com/method/{method}'
        cities_list = requests.get(url, params=params).json()['response']['items']
        return cities_list

    def get_user_info(self, user_id):
        #получение информации о пользователе
        method = 'users.get'
        params = {
            'user_id': user_id,
            'fields': 'sex, bdate, city, relation, last_seen',
            'v': '5.131',
            'access_token': self.user_token
        }
        url = f'https://api.vk.com/method/{method}'
        res = requests.get(url, params=params).json()
        if 'response' in res and 'error' not in res:
            return res['response'][0]
        else:
            return None

    def get_popular_photos(self, user_id):
        #получение идентификаторов фотографий и их сортировка по популярности
        method = 'photos.get'
        params = {'user_id': user_id,
                  'access_token': user_token,
                  'album_id': 'profile',
                  'extended': 1,
                  'v': '5.131'}
        url = f'https://api.vk.com/method/{method}'
        res = requests.get(url, params=params).json()
        photo_kit = {}
        try:
            photos = res['response']['items']
            if not photos:
                return None
            popular_photos = sorted(
                photos,
                key=lambda k: k['likes']['count'] + k['comments']['count'],
                reverse=True
            )[0:3]
            for photo in popular_photos:
                if 'owner_id' not in photo_kit.keys():
                    photo_kit['owner_id'] = photo['owner_id']
                    photo_kit['pics_ids'] = []
                photo_kit['pics_ids'].append(photo['id'])

        except KeyError:
            pass

        finally:
            return photo_kit
