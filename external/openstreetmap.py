import io
from typing import Tuple, List

import aiohttp
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt


async def nominatim_query(params: dict, reverse: bool = False) -> dict | None:
    endpoint = "reverse" if reverse else "search"

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://nominatim.openstreetmap.org/{endpoint}",
                               params=params,
                               headers={
                                   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                                 "(KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36"
                               }) as response:
            if response.status == 200:
                json_response = await response.json()
                return json_response
            return None


async def get_country(country: str) -> dict | None:
    params = {"q": country,
              "format": "json",
              "language": "ru"}

    json_response = await nominatim_query(params)
    if json_response:
        for item in json_response:
            if item["addresstype"] == "country":
                return {"name": item["name"]}
    return None


async def get_city(country: str, city: str) -> dict | None:
    query = f"{city}, {country}"

    params = {"q": query,
              "format": "json",
              "language": "ru"}

    json_response = await nominatim_query(params)

    if json_response:
        for item in json_response:
            if item["type"] == "city" or item["addresstype"] == "city":
                return {
                    "name": item["name"],
                    "latitude": item["lat"],
                    "longitude": item["lon"]
                }
    return None


async def process_location(latitude: float, longitude: float) -> dict:
    params = {"lat": latitude,
              "lon": longitude,
              "format": "json",
              "language": "ru"}

    json_response = await nominatim_query(params, reverse=True)

    if json_response:
        address = json_response.get("address", {})

        country = address.get("country", None)

        city = (address.get("city", None) or
                address.get("town", None) or
                address.get("village", None))

        return {"country": country, "city": city}

    return {"country": None, "city": None}


async def plot_route(coordinates: List[Tuple[float, float]]) -> bytes:
    """
    Функция принимает список кортежей с координатами (широта, долгота) и возвращает изображение маршрута.
    """
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.PlateCarree()})
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=":")

    latitudes, longitudes = zip(*coordinates)

    ax.plot(longitudes, latitudes, marker="o", color="red", markersize=5, linestyle="-", transform=ccrs.Geodetic())

    ax.set_extent([min(longitudes) - 1, max(longitudes) + 1, min(latitudes) - 1, max(latitudes) + 1],
                  crs=ccrs.PlateCarree())

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return buf.read()
