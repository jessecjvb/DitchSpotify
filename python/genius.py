import os
import re
from lyricsgenius import Genius
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv, find_dotenv

# 1. Load the variables from .env into Python's environment
load_dotenv(find_dotenv())

# Replace with your actual Genius Client Access Token
# GENIUS_ACCESS_TOKEN = "YOUR_GENIUS_ACCESS_TOKEN"
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_CLIENT_ACCESS_CODE")

# Initialize Genius client (configured to skip non-song results and headers like [Chorus])
genius = Genius(GENIUS_ACCESS_TOKEN, remove_section_headers=True, skip_non_songs=True, timeout=5, retries=3)

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# 2. Input Data
songs_input = [
    ("Queen", "Bohemian Rhapsody"),
    ("Pharrell Williams", "Happy"),
    ("Johnny Cash", "Hurt"),
    ("Kendrick Lamar", "HUMBLE.")
]

def clean_lyrics(text):
    """Remove boilerplate tags and extra whitespace from scraped lyrics."""
    if not text:
        return ""
    # Remove contributor counts and 'Lyrics' suffix often appended by Genius
    text = re.sub(r'^\d* ?Contributor[s]?.*Lyrics', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'Embed$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+$', '', text) # Remove trailing numbers
    return text.strip()

def analyze_sentiment(text):
    """Returns VADER compound score and categorical classification."""
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    
    if compound >= 0.05:
        category = "Positive"
    elif compound <= -0.05:
        category = "Negative"
    else:
        category = "Neutral"
        
    return compound, category

def extract_subject_keywords(corpus, max_keywords=5):
    """Uses TF-IDF to identify the most defining thematic words across the fetched songs."""
    # Custom stop words to filter out common vocalizations in music
    music_stopwords = ["oh", "ah", "yeah", "la", "na", "ooh", "da", "gonna", "wanna", "gotta", "verse", "chorus"]
    
    vectorizer = TfidfVectorizer(
        stop_words='english', 
        max_features=1000, 
        ngram_range=(1, 2) # Capture single words and two-word phrases
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
        feature_names = vectorizer.get_feature_names_out()
        
        keywords_per_song = []
        for row in tfidf_matrix:
            # Sort words by their TF-IDF weight in descending order
            sorted_indices = row.toarray()[0].argsort()[::-1]
            top_words = [feature_names[i] for i in sorted_indices[:max_keywords] if row.toarray()[0][i] > 0]
            # Filter out custom music stopwords
            clean_words = [w for w in top_words if w.lower() not in music_stopwords]
            keywords_per_song.append(clean_words[:max_keywords])
            
        return keywords_per_song
    except ValueError:
        return [["N/A"] for _ in corpus]

# 3. Pipeline Execution
# print("Fetching lyrics and processing NLP pipeline...\n" + "="*50)

# fetched_songs = []
# lyrics_corpus = []

# for artist, title in songs_input:
#     print(f"Searching: {title} by {artist}...")
#     song_data = genius.search_song(title, artist)
    
#     if song_data and song_data.lyrics:
#         cleaned = clean_lyrics(song_data.lyrics)
#         fetched_songs.append((artist, title, cleaned))
#         lyrics_corpus.append(cleaned)
#     else:
#         print(f" -> Could not find lyrics for {title} by {artist}.")

# # Extract keywords across all retrieved lyrics
# subject_keywords = extract_subject_keywords(lyrics_corpus)

# 3. Pipeline Execution
print("Fetching and printing lyrics...\n" + "="*50)

fetched_songs = []
lyrics_corpus = []

for artist, title in songs_input:
    print(f"\nSearching: {title} by {artist}...")
    
    try:
        song_data = genius.search_song(title, artist)
        
        if song_data and song_data.lyrics:
            cleaned = clean_lyrics(song_data.lyrics)
            fetched_songs.append((artist, title, cleaned))
            lyrics_corpus.append(cleaned)
            
            # --- PRINT TEST BLOCK ---
            print(f"\n--- LYRICS FOR: {title} by {artist} ---")
            print(cleaned)
            print("-" * 50)
            
        else:
            print(f" -> Could not find lyrics for {title} by {artist}.")
            
    except (Timeout, RequestException) as e:
        print(f" -> [Skipped] Network timeout while fetching '{title}' by {artist}.")
        continue
    except Exception as e:
        print(f" -> [Skipped] Unexpected error for '{title}': {e}")
        continue

# 4. Results Output
print("\n" + "="*50 + "\nANALYSIS RESULTS\n" + "="*50)

for i, (artist, title, lyrics) in enumerate(fetched_songs):
    score, sentiment_label = analyze_sentiment(lyrics)
    keywords = subject_keywords[i]
    
    print(f"\nSong: {title} - {artist}")
    print(f"Sentiment:  {sentiment_label} (Compound Score: {score:.3f})")
    print(f"Key Themes: {', '.join(keywords)}")
    print("-" * 50)