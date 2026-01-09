import requests
import base64
import time      
import pandas as pd 
from pprint import pprint

def refresh_access_token(refresh_token, client_id, client_secret):
    """Diese Funktion sendet einen POST-Request an `/api/token` 
    und liefert den aktualisierten Access Token für die App.

    Args:
        refresh_token (str)

    Returns:
        str: Der Access Token (`None`, wenn die Anfrage versagt)
    """
    
    auth_url = "https://accounts.spotify.com/api/token"
    
    # Spotify erwartet die Client-ID und den Client-Secret in Base64-codiertem Format im Authorization-Header.
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'authorization': f'Basic {b64_auth_str}'
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = requests.post(auth_url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Fehler: {response.status_code}")
        print(response.json())
        return None

def get_spotify_ids(track_name, artist_name, token):
    """Sucht Track- und Artist_ID für eine Namen-Kombination."""

    search_url="https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Gezielt nach Track + Artist suchen
    params = {
        "q": f"track:{track_name} artist:{artist_name}",
        "type": "track",
        "limit": 1
    }
    
    try:
        res = requests.get(search_url, headers=headers, params=params)
        if res.status_code == 200:
            items = res.json().get('tracks', {}).get('items', [])
            if items:
                track_id = items[0]['id']
                artist_id = items[0]['artists'][0]['id']
                return track_id, artist_id
    except Exception as e:
        print(f"Fehler bei {track_name}: {e}")
    return None, None

def get_artists_batch(id_list, token):
    """Holt Genres, Follower und Popularität für bis zu 50 IDs via Query-Params."""
    url = "https://api.spotify.com/v1/artists"
    headers = {"Authorization": f"Bearer {token}"}
    
    # requests.get baut mit 'params' automatisch das richtige ?ids=ID1,ID2 Format
    params = {"ids": ",".join(id_list)}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('artists', [])
    else:
        print(f"Fehler Artist-Batch: {response.status_code}")
        return []

def get_tracks_batch(id_list, token):
    """Holt Release-Datum, Popularity und Explicit-Flag für bis zu 50 IDs."""
    url = "https://api.spotify.com/v1/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"ids": ",".join(id_list)}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('tracks', [])
    else:
        print(f"Fehler Track-Batch: {response.status_code}")
        return []
