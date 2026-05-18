import requests
import os
from io import BytesIO
from flask import current_app


def get_map_image(address, filename):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "8013b162-6b42-4997-9691-77b7074026e0",
        "geocode": address,
        "format": "json"
    }

    response = requests.get(geocoder_api_server, params=geocoder_params)
    if not response:
        return None

    json_response = response.json()

    feature = json_response["response"]["GeoObjectCollection"]["featureMember"]
    if not feature:
        return None

    toponym = feature[0]["GeoObject"]
    lon, lat = toponym["Point"]["pos"].split()

    map_api_server = "https://static-maps.yandex.ru/v1"

    map_params = {
        "ll": f"{lon},{lat}",
        "z": 15,
        "size": "450,450",
        "apikey": "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13",
        "pt": f"{lon},{lat},pm2rdm"
    }

    response = requests.get(map_api_server, params=map_params)

    # print(response.url)
    # print(response.text)

    if not response:
        return None

    folder = os.path.join(current_app.root_path, "static", "maps")
    # folder = os.path.join(os.getcwd(), "static", "maps")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(response.content)

    return f"maps/{filename}"


# if __name__ == "__main__":
#     import uuid

#     filename = f"{uuid.uuid4()}.png"

#     result = get_map_image("Москва, Красная площадь", filename)

#     print("RESULT:", result)