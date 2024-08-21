import aiohttp

from config import config


async def get_weather(lat: float,
                      lon: float):
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    async with aiohttp.ClientSession() as session:
        params = {
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "appid": config.OPENWEATHERMAP_API.get_secret_value(),
            "lang": "ru"
        }

        response = await session.get(base_url, params=params)

        return await response.json()
