import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv, find_dotenv

# 1. Load the variables from .env into Python's environment
load_dotenv(find_dotenv())

print("Client ID found:", os.getenv("SPOTIPY_CLIENT_ID"))

# 2. Request access to both listening history and private playlists
SCOPES = "user-read-recently-played playlist-read-private"

# 3. Initialize Spotipy (it will now automatically find the SPOTIPY_ variables we just loaded!)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPES))

# --- Test Fetching Recently Played Tracks ---
print("--- Recently Played Tracks ---")
recently_played = sp.current_user_recently_played(limit=20)
for item in recently_played['items']:
    track = item['track']
    artist_name = track['artists'][0]['name']
    print(f"{track['name']} by {artist_name}")

# --- Test Fetching User Playlists ---
print("\n--- User Playlists ---")
playlists = sp.current_user_playlists(limit=20)
for playlist in playlists['items']:
    print(f"{playlist['name']} ({playlist['items']['total']} tracks)")


if not playlists['items']:
    print("No playlists found on this account.")
else:
    first_playlist = playlists['items'][10]
    playlist_id = first_playlist['id']
    playlist_name = first_playlist['name']

    print(f"=== Songs in Playlist: '{playlist_name}' ===")

    # 4. Fetch playlist items
    results = sp.playlist_items(playlist_id)
    items = results.get('items', [])

    if not items:
        print("This playlist appears to be empty or contains restricted media!")
    else:
        for index, item in enumerate(items, start=1):
            # Safe extraction for tracks vs episodes vs local files
            track = item.get('track') or item.get('item')
            
            if track:
                track_name = track.get('name', 'Unknown Title')
                
                # Check for artists (tracks have artists, podcast episodes have show info)
                if 'artists' in track and track['artists']:
                    artists = ", ".join([a['name'] for a in track['artists']])
                    print(f"{index}. {track_name} — {artists}")
                else:
                    print(f"{index}. {track_name}")
            else:
                print(f"{index}. [Unavailable track or local file]")