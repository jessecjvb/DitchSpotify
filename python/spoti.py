import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv, find_dotenv

def get_recently_played_tracks(sp, limit=50):
    """Fetch user's recently played track items."""
    try:
        recently_played = sp.current_user_recently_played(limit=limit)
        return recently_played.get('items', [])
    except Exception as e:
        print(f"Error fetching recently played tracks: {e}")
        return []


def get_liked_tracks(sp, max_tracks=100):
    """Fetch user's liked tracks up to a maximum limit."""
    all_liked_tracks = []
    limit = min(50, max_tracks)
    
    try:
        results = sp.current_user_saved_tracks(limit=limit)
        
        while results and len(all_liked_tracks) < max_tracks:
            for item in results.get('items', []):
                track = item.get('track')
                if track:
                    artist_name = track['artists'][0]['name']
                    track_name = track['name']
                    all_liked_tracks.append(f"{artist_name} - {track_name}")
                    
                    if len(all_liked_tracks) >= max_tracks:
                        break

            # Fetch the next page if needed
            if len(all_liked_tracks) < max_tracks and results.get('next'):
                results = sp.next(results)
            else:
                results = None
                
    except Exception as e:
        print(f"Error fetching liked tracks: {e}")
        
    return all_liked_tracks


def fetch_all_user_tracks(sp, max_liked=100, recently_played_limit=50):
    """
    Main function to aggregate liked and recently played tracks.
    Returns a combined list containing formatted liked track strings 
    and recently played track item objects.
    """
    recently_played_items = get_recently_played_tracks(sp, limit=recently_played_limit)
    liked_tracks = get_liked_tracks(sp, max_tracks=max_liked)

    print(f"Retrieved {len(recently_played_items)} recently played tracks.")
    print(f"Retrieved {len(liked_tracks)} liked tracks.")

    all_tracks = liked_tracks + recently_played_items
    return all_tracks