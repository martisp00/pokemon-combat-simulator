import requests
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://pokeapi.co/api/v2"

# Module-level session for connection pooling across threads
_session = requests.Session()
_session.headers.update({"User-Agent": "pokemon-combat-sim/1.0"})

# Module-level move cache (safe to use from threads, unlike @st.cache_data)
_move_cache: dict = {}


def _get_json(url):
    try:
        r = _session.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException:
        return None


@st.cache_data
def get_pokemon(name):
    if not name:
        return None
    return _get_json(f"{BASE_URL}/pokemon/{name.strip().lower()}")


@st.cache_data
def get_type(name):
    if not name:
        return None
    return _get_json(f"{BASE_URL}/type/{name.strip().lower()}")


def _fetch_move(move_name):
    """Fetch a single move. Uses module-level dict cache (thread-safe reads)."""
    if move_name in _move_cache:
        return _move_cache[move_name]

    move_data = _get_json(f"{BASE_URL}/move/{move_name}")
    if not move_data:
        _move_cache[move_name] = None
        return None

    power = move_data.get("power")
    if power is None:
        _move_cache[move_name] = None
        return None

    result = {
        "name": move_data["name"],
        "power": power,
        "type": move_data["type"]["name"],
        "pp": move_data.get("pp", 10),
        "damage_class": move_data.get("damage_class", {}).get("name", ""),
    }
    _move_cache[move_name] = result
    return result


@st.cache_data
def get_damaging_moves_for_pokemon(pokemon_name: str):
    pokemon_json = get_pokemon(pokemon_name)
    if not pokemon_json:
        return []

    move_names = [e["move"]["name"] for e in pokemon_json.get("moves", [])]

    moves = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(_fetch_move, name): name for name in move_names}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                moves.append(result)

    moves.sort(key=lambda x: x["power"], reverse=True)
    return moves


@st.cache_data
def get_all_pokemon_names(limit=151):
    data = _get_json(f"{BASE_URL}/pokemon?limit={limit}&offset=0")
    if not data:
        return []
    return [p["name"] for p in data.get("results", [])]
