import os
import requests
from geopy.distance import distance, lonlat
from dotenv import load_dotenv

load_dotenv()


def fetch_coordinates_from_api(address):
    apikey = os.getenv('SECRET_KEY')
    if not apikey:
        return None

    base_url = "https://geocode-maps.yandex.ru/1.x"
    try:
        response = requests.get(base_url, params={
            'geocode': address,
            'apikey': apikey,
            'format': 'json',
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]['GeoObject']
        lon, lat = most_relevant['Point']['pos'].split(" ")
        return float(lon), float(lat)
    except (requests.RequestException, KeyError, ValueError, IndexError):
        return None


def get_coordinates(address):
    if not address:
        return None

    from foodcartapp.models import Geocache

    cached_location = Geocache.objects.filter(address=address).first()
    if cached_location and cached_location.lon and cached_location.lat:
        return cached_location.lon, cached_location.lat

    coords = fetch_coordinates_from_api(address)

    if coords:
        lon, lat = coords
        Geocache.objects.update_or_create(
            address=address,
            defaults={'lon': lon, 'lat': lat}
        )
        return coords

    Geocache.objects.get_or_create(
        address=address,
        defaults={'lon': None, 'lat': None}
    )
    return None


def calculate_distance(coords1, coords2):
    if not coords1 or not coords2:
        return None
    return distance(lonlat(*coords1), lonlat(*coords2)).km
