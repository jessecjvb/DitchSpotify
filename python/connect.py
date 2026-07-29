import spotipy
from spotipy.oauth2 import SpotifyOAuth
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import os
import json
import time
import syncedlyrics
from dotenv import load_dotenv, find_dotenv

from python import spoti
from python import ai
from python import lyrics

def run_spotify_ai(sp):
    """
    Takes an authenticated spotipy.Spotify object and returns the AI winner data.
    """

    try:
        # Fetch 20 recently played + liked songs using the authenticated client
        all_tracks = spoti.fetch_all_user_tracks(sp, max_liked=100, recently_played_limit=20)

        # Find top 5 best songs
        target_songs = ai.select_top_candidate_songs(all_tracks)
        
        # Fetch lyrics
        lyric_dict = lyrics.fetch(target_songs)

        # Crown the winner
        winner = ai.select_best_song(lyric_dict)

        # Return a dictionary instead of printing, so Flask can send it to the frontend
        return {
            "status": "success",
            "winning_song": winner.winning_song,
            "theme": winner.theme,
            "explanation": winner.explanation
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }

def main():
    # load env variables
    load_dotenv()
    # find recently played + liked songs
    SCOPES = "user-library-read user-read-recently-played"
    # 3. Initialize Spotipy
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPES))
    # 20 recently played + liked songs
    all_tracks = spoti.fetch_all_user_tracks(sp, max_liked=100, recently_played_limit=20)

    # Find top 5 best songs to find lyrics for
    try:
        target_songs = ai.select_top_candidate_songs(all_tracks)
    except Exception as e:
        print(f"An error occured while selecting songs! Please try again later. \n{e}")
        return f"An error occured while selecting songs! Please try again later. \n{e}"


    # Fetch lyrics of five top songs
    lyric_dict = lyrics.fetch(target_songs)

    print(lyric_dict)

    print("Analyzing lyrics and crowning the winner...\n")

    try:
        # Call your function
        winner = ai.select_best_song(lyric_dict)

        # Access the clean data directly through Python attributes
        print(f"Je hebt recentelijk geluisterd naar {winner.winning_song}.")
        # print(f"📌 THEME: {winner.theme}")
        print(f"{winner.explanation}")
        if winner.theme.lower() == "anti-war":
            print(f"De betekenis van dit nummer staat haaks op de investeringen van Spotify's voorzitter")
        elif winner.theme.lower() == "climate change warning":
            print("De betekenis van dit nummer staat haaks op de technologie die Spotify gebruikt")

    except Exception as e:
        print(f"An error occured during evaluation! Please try again later. \n{e}")
        return f"An error occured during evaluation! Please try again later. \n{e}"

if __name__ == "__main__":
    main()