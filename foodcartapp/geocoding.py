import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_coordinates(address):
    api_key = os.getenv('SECRET_KEY')
    if not api_key:
        return None
    url = 'https://geocode-maps.yandex.ru/v1'
    params = {
        'apikey': api_key,
        'geocode': address,
        'format': 'json',
        'lang': 'ru_RU',
    }
    try:
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
    except (requests.RequestException, KeyError, ValueError, IndexError):
        return None


