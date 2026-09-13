import requests
import os
import math
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


def calculate_distance(from_coords, to_coords):
    if not from_coords or not to_coords:
        return None

    lon1, lat1 = from_coords
    lon2, lat2 = to_coords

    radius = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(radius * c, 2)
