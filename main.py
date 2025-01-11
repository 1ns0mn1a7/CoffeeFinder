import json
import os

import requests
from dotenv import load_dotenv
from geopy import distance
import folium


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = (
        response.json()['response']
        ['GeoObjectCollection']
        ['featureMember']
    )

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def load_coffee_shops(file_path, encoding="CP1251"):
    with open(file_path, "r", encoding=encoding) as my_file:
        coffee_contents = my_file.read()
    return json.loads(coffee_contents)


def calculate_distances(user_coordinates, coffee_shops):
    new_coffee_shops = []
    for shop in coffee_shops:
        name_shop = shop['Name']
        longitude, latitude = shop['geoData']['coordinates']
        shop_coordinates = (latitude, longitude)
        shop_distance = (
            distance.distance(user_coordinates, shop_coordinates).km
        )
        new_coffee_shops.append({
            'title': name_shop,
            'distance': shop_distance,
            'latitude': latitude,
            'longitude': longitude,
        })
    return new_coffee_shops


def find_nearest_coffee_shops(coffee_shops, top_n=5):
    sorted_coffee_shops = sorted(coffee_shops, key=lambda x: x['distance'])
    return sorted_coffee_shops[:top_n]


def create_map(user_coordinates, nearest_shops):
    m = folium.Map(location=user_coordinates, zoom_start=14)

    folium.Marker(
        location=user_coordinates,
        popup="Ваше местоположение",
        icon=folium.Icon(color="blue")
    ).add_to(m)

    for shop in nearest_shops:
        folium.Marker(
            location=(shop['latitude'], shop['longitude']),
            popup=shop['title'],
            icon=folium.Icon(color="green")
        ).add_to(m)

    m.save("map.html")


def main():
    load_dotenv()
    apikey = os.getenv("Yandex_API")
    my_position = input("Где вы находитесь?: ")
    lon, lat = fetch_coordinates(apikey, my_position)
    user_coordinates = (lat, lon)
    print(f"Ваши координаты: {user_coordinates}")
    coffee_shops = load_coffee_shops("coffee.json")
    coffee_shops_with_distances = calculate_distances(
        user_coordinates,
        coffee_shops
    )
    nearest_shops = find_nearest_coffee_shops(coffee_shops_with_distances)
    create_map(user_coordinates, nearest_shops)


if __name__ == "__main__":
    main()
