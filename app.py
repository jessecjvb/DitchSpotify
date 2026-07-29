import os
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from python.connect import run_spotify_ai # Import your updated function
import python.lyrics
import python.spoti
import python.ai


app = Flask(__name__)

# Set the secret key for session management
app.secret_key = os.getenv("FLASK_SECRET_KEY", "a_fallback_secret_key_for_local_dev")

# Helper function to configure Spotify OAuth
def create_spotify_oauth():
    cache_handler = FlaskSessionCacheHandler(session)
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-library-read user-read-recently-played",
        cache_handler=cache_handler,
        show_dialog=True
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/connect")
def connect():
    cache_handler = FlaskSessionCacheHandler(session)
    auth_manager = create_spotify_oauth()
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(url_for('login'))
        
    return render_template("connect.html")

@app.route("/login")
def login():
    auth_manager = create_spotify_oauth()
    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    auth_manager = create_spotify_oauth()
    auth_manager.get_access_token(request.args.get("code"))
    return redirect(url_for("connect"))

@app.route("/api/run_ai")
def api_run_ai():
    # This is the endpoint the frontend will call behind the scenes
    cache_handler = FlaskSessionCacheHandler(session)
    auth_manager = create_spotify_oauth()
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    # Create the authenticated Spotify client
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Run your AI logic
    result = run_spotify_ai(sp)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)