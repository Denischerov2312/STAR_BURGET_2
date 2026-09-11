import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_coordinates(address, apikey):
    url = 'https://geocode-maps.yandex.ru/v1'
    params = {
        'apikey': apikey,
        'geocode': address,
        'format': 'json',
        'lang': 'ru_RU',
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    geo_objects = response.json()['response']['GeoObjectCollection'][
        'featureMember'
    ]
    if not geo_objects:
        return None
    pos = geo_objects[0]['GeoObject']['Point']['pos']
    lon, lat = pos.split(' ')
    return float(lon), float(lat)


api_key = os.getenv('SECRET_KEY')
address = 'проспект Гагарина, 94, Нижний Новгород'
coordinates = get_coordinates(address, api_key)
print(coordinates)