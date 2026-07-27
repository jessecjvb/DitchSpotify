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

import lyrics
import spoti
import ai

# load env variables
load_dotenv()
# find recently played + liked songs
SCOPES = "user-library-read user-read-recently-played"
# 3. Initialize Spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPES))
# 20 recently played + liked songs
all_tracks = spoti.fetch_all_user_tracks(sp, max_liked=100, recently_played_limit=20)

# Find top 5 best songs to find lyrics for
target_songs = ai.select_top_candidate_songs(all_tracks)


# Fetch lyrics of five top songs
lyric_dict = lyrics.fetch(target_songs)

print(lyric_dict)

print("Analyzing lyrics and crowning the winner...\n")

try:
    # Call your function
    winner = ai.select_best_song(lyric_dict)

    # Access the clean data directly through Python attributes
    print(f"🏆 WINNER: {winner.winning_song}")
    print(f"📌 THEME: {winner.theme}")
    print(f"💬 KEY LYRICS: \"{winner.key_quote}\"")
    print(f"📖 WHY IT WON:\n{winner.explanation}")

except Exception as e:
    print(f"An error occurred during evaluation: {e}")