import os
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from python.connect import run_spotify_ai # Import your updated function
# import python.lyrics
# import python.spoti
# import python.ai

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

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

# Landing page before logging in
@app.route("/connect")
def connect():
    return render_template("connect.html")

# Redirect to Spotify
@app.route("/login")
def login():
    auth_manager = create_spotify_oauth()
    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)

# Page after log in
@app.route("/callback")
def callback():
    auth_manager = create_spotify_oauth()
    code = request.args.get("code")
    if code:
        auth_manager.get_access_token(code)
    # Redirect straight to the thinking page
    return redirect(url_for("thinking"))

# The thinking page that runs the AI computation
@app.route("/thinking")
def thinking():
    cache_handler = FlaskSessionCacheHandler(session)
    auth_manager = create_spotify_oauth()
    
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(url_for('connect'))
        
    # Check if we should execute the AI run
    if request.args.get("run") == "true":
        sp = spotipy.Spotify(auth_manager=auth_manager)
        # Run your python script
        ai_data = run_spotify_ai(sp)
        # Store result in session to pass to the final result page
        session['ai_result'] = ai_data
        return redirect(url_for("result"))

    return render_template("thinking.html")

# Final page showing the output
@app.route("/result")
def result():
    ai_data = session.get('ai_result', {})
    return render_template("result.html", data=ai_data)

if __name__ == "__main__":
    app.run(debug=True)