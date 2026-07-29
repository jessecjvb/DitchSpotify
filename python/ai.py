import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv

# 1. Define the exact shape you want Gemini to return
class SongSelection(BaseModel):
    songs_to_fetch_lyrics: list[str] = Field(
        description="A list of up to 5 song titles (formatted as 'Artist - Title') to fetch lyrics for."
    )

def select_top_candidate_songs(all_tracks: list, client: genai.Client = None) -> list[str]:
    """
    Evaluates a list of tracks using Gemini structured outputs to select up to 5 songs
    with the heaviest anti-war or climate change themes.
    
    Returns a list of formatted song strings ('Artist - Title').
    """
    if client is None:
        # 2. Initialize the client (automatically uses GEMINI_API_KEY from environment)
        client = genai.Client(
            http_options=types.HttpOptions(timeout=100_000)
        )

    # 3. Construct a prompt instructing the model to prefer internal memory
    prompt = f"""
FAST HEURISTIC SCAN:
Scan the following song list and immediately pick UP TO 5 songs that have the most severe anti-war messages or urgent climate change warnings.

Selection Weights:
- 85%: The song's lyrics (based on your internal memory).
- 10%: The literal meaning and tone of the song title.
- 5%: The band or artist's historical reputation for political or environmental themes.

CRITICAL SPEED RULES:
- Do NOT deeply compare or analyze every song.
- Do NOT search for unknown songs; ignore any track you do not instantly recognize.
- Output ONLY the selected list matching the JSON schema immediately.

Song List:
{chr(10).join(all_tracks)}
"""

    print("Filtering top 5 lyric candidates...\n")

    try:
        # 4. Execute the request using gemini-3.5-flash
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SongSelection,
                temperature=0.1
            )
        )

        # 5. Validate and extract the pure Python list
        data = SongSelection.model_validate_json(response.text)
        
        # This is your clean Python list, ready to loop through your Lyric API:
        target_songs = data.songs_to_fetch_lyrics
        
        print("=== READY FOR LYRIC API ===")
        print(f"Type: {type(target_songs)}")
        print("List:", target_songs)

        return target_songs

    except Exception as e:
        print(f"\nAn error occurred (no freeze!): {e}")
        raise Exception(e)

class WinningSongAnalysis(BaseModel):
    winning_song: str = Field(
        description="The artist and title of the selected winning song."
    )
    theme: str = Field(
        description="The primary theme: 'Anti-War' or 'Climate Change Warning'."
    )
    explanation: str = Field(
        description="A concise summary written in Dutch explaining how the song addresses the chosen topic with strength and urgency, without referencing or comparing it to the other candidate songs."
    )

def select_best_song(results: list[dict], client: genai.Client = None) -> WinningSongAnalysis:
    """
    Takes a list of lyric lookup results, feeds them to Gemini, 
    and returns the song with the heaviest anti-war or climate warning message.
    """
    # Initialize the client with a 60-second timeout if one wasn't passed in
    if client is None:
        client = genai.Client(http_options=types.HttpOptions(timeout=60_000))

    # Step A: Format the dictionary list into a clean text block for the LLM
    formatted_context = ""
    for item in results:
        song_title = item.get("song", "Unknown Song")
        success = item.get("success", False)
        lrc = item.get("lrc_data", "")

        formatted_context += f"CANDIDATE: {song_title}\n"
        
        # If lyrics were found, feed them. If not, tell the AI to use its memory.
        if success and lrc:
            formatted_context += f"LYRICS:\n{lrc}\n"
        else:
            formatted_context += "LYRICS: [Lookup Failed — Evaluate based on internal knowledge if familiar]\n"

    # Step B: Build the evaluation prompt
    prompt = f"""
    You are an expert thematic music analyst. Review the following candidate songs and their lyrics.
    Select the SINGLE song with the heaviest, most explicit, and impactful anti-war message or climate change warning.

    Candidate Songs & Lyrics:
    {formatted_context}

    Instructions:
    1. Base your decision primarily on the emotional urgency, lyric intensity, and specificity of the message.
    2. If a song's lyrics failed to load, you may evaluate it based on your internal knowledge of the track.
    3. In the 'explanation' field, describe why and how this specific song conveys its theme with such strength and urgency. Write this explanation in DUTCH.
    4. Do NOT compare the winning song to the other candidate songs or mention the existence of other songs in the list (e.g., avoid phrases like "Unlike the other songs" or "This song beat the rest"). Focus strictly on the isolated merits of the selected song.
    5. Return your final choice strictly adhering to the JSON schema provided.
    """

    # Step C: Call the model with structured output enabled
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=WinningSongAnalysis,
            temperature=0.2  # Keep low for analytical consistency
        )
    )

    # Step D: Convert the JSON response into our Pydantic object and return it
    return WinningSongAnalysis.model_validate_json(response.text)
