import random
from typing import List

import aiohttp

from config import config


async def search_places(latitude: float | str,
                        longitude: float | str,
                        category_name: str,
                        radius=5000) -> List[dict]:
    match category_name:
        case "landmarks":
            categories = "16000"
        case "hotels":
            categories = "19014"
        case "food":
            categories = "13134,13338,13344"
        case _:
            categories = ""

    url = "https://api.foursquare.com/v3/places/search"

    headers = {
        "Accept": "application/json",
        "Authorization": config.FOURSQUARE_API.get_secret_value()
    }

    params = {
        "ll": f"{latitude},{longitude}",
        "categories": categories,
        "radius": radius,
        "limit": 15,
        "fields": "name,location,description,rating"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            parsed_response = await response.json()

            names = []

            final_results = []

            for result in parsed_response["results"]:
                if "address" in result["location"] and result["name"] not in names:
                    final_results += [
                        {
                            "name": result["name"],
                            "description": result["description"] if "description" in result else None,
                            "address": result["location"]["address"],
                            "rating": result["rating"]
                        }
                    ]

                names += [result["name"]]

            random.shuffle(final_results)

            return final_results[:5]
