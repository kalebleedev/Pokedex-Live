import random 
import re

import requests
from django.core.cache import cache

API_URL = "https://pokeapi.co/api/v2"
SPRITE_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
    "sprites/pokemon/{id}.png"
)

CACHE_SECONDS = 300
TIMEOUT_SECONDS = 8
MAX_POKEMON_ID = 1025

class PokeAPIError(Exception):
    """PokeAPI could not be reached or sent back something unexpected."""

# PokemonNotFound uses PokeAPIError Class for exception handling
class PokemonNotFound(PokeAPIError):
    """The Pokemon we asked for does not exist."""

def _get(path):
    """Fetch the JSON from PokeAPI, turning problems into our own errors."""
    try:
        # Response -> response for API_URL / PATH
        response = requests.get(f"{API_URL}/{path}", timeout=TIMEOUT_SECONDS)
    except requests.RequestException as error:
        # if not -> Error
        raise PokeAPIError("Could not reach PokeAPI") from error

    # 404 -> Not Found
    if response.status_code == 404:
        raise PokemonNotFound(path)
    # 200 -> Ok - anything else - no
    if response.status_code != 200:
        raise PokeAPIError(f"PokeAPI returned {response.status_code}")
    return response.json()

def clean_name(name):
    """Lowercase the name and make sure it is safe to put into the url."""
    # turns into string, strip whitespace, lowercase, replaces space with -
    name = str(name).strip().lower().replace(" ", "-")
    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise PokemonNotFound(name)
    return name

# Function to input the pokemon id into SPRITE_URL
def sprite_url(pokemon_id):
    return SPRITE_URL.format(id=pokemon_id)
"""
            types = []
            for t in raw["types]:
                pokemon_type = t["type]["name]
                types.append(pokemon_type)
"""
"""
            stats = {}
            for s in raw["stats"]:
                stat_name = s["stat"]["name"]
                stat_value = s["base_stat]
                stats[stat_name] = stat_value
"""
def get_pokemon(name):
    """Return the details for one Pokemon"""
    name = clean_name(name)
    key = f"pokemon:{name}"
    pokemon = cache.get(key)
    if pokemon is not None:
        return pokemon

    raw = _get(f"pokemon/{name}")
    sprites = raw["sprites"]
    artwork = sprites.get("other", {}).get("official-artwork", {})
    pokemon = {
        "id": raw["id"],
        "name": raw["name"],
        "height": raw["height"] / 10,
        "weight": raw["weight"] / 10,
       
        "type": [t["type"]["name"] for t in raw["types"]],
        "abilities": [a["ability"]["name"] for a in raw["abilities"]],
        # {"Hp": 35, "Attack": 40, etc.....}
        "stats": {s["stat"]["name"]: s["base_stat"] for s in raw["stats"]},
        "images": artwork.get("front_default") or sprites.get("front_default")
    }
    cache.set(key, pokemon, CACHE_SECONDS)
    return pokemon

def get_pokemon_page(page=1, per_page=20):
    """Return one page of the Pokemon List."""
    offset = (page - 1) * per_page
    key = f"page:{offset}:{per_page}"
    data = cache.get(key)
    if data is not None:
        return data
    raw = _get(f"pokemon?limit={per_page}&offset={offset}")
    
    results = []
    for item in raw["results"]:
        pokemon_id = int(item["url"].rstrip("/").split("/")[-1])
        results.append({
            "id": pokemon_id,
            "name": item["name"],
            "image": sprite_url(pokemon_id)
        })

    data = {
        "results": results,
        "has_next": raw["next"] is not None,
        "has_previous": raw["previous"] is not None,
    }

    cache.set(key, data, CACHE_SECONDS)
    return data

def get_random_pokemon():
    return get_pokemon(random.randint(1, MAX_POKEMON_ID))
    

# if __name__ == "__main__":

