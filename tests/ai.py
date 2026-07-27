import os
from google import genai
from google.genai import types
from dotenv import load_dotenv, find_dotenv

# 1. Load the variables from .env into Python's environment
load_dotenv()

# 1. Initialize the client (automatically uses GEMINI_API_KEY from environment)
client = genai.Client()

print("Models available to your API key:\n")
for model in client.models.list():
    # Show models that support content generation
    if "generateContent" in model.supported_actions:
        print(f"- {model.name}")

# 2. Sample song list (you can scale this up to 1,000 songs)
songs = [
    "Black Sabbath - War Pigs",
    "Michael Jackson - Earth Song",
    "Edwin Starr - War",
    "Midnight Oil - Beds Are Burning",
    "Joni Mitchell - Big Yellow Taxi",
    "Creedence Clearwater Revival - Fortunate Son",
    "Anohni - 4 Degrees",
    "Bob Dylan - Masters of War",
    "Nena - 99 Luftballons",
    "Childish Gambino - Feels Like Summer"
]

# 3. Construct a prompt instructing the model to prefer internal memory
prompt = f"""
You are an expert musicologist and thematic analyst. 
Analyze the following list of songs and select the SINGLE song with the heaviest anti-war message or climate change warning.

Song List:
{chr(10).join(songs)}

Instructions:
1. Rely on your internal knowledge for familiar songs.
2. ONLY trigger Google Search if you encounter an obscure song whose lyrics or context you do not know. Do NOT search for well-known songs.
3. State your winner clearly, summarize its core theme, and quote 1-2 key lyrics as evidence.
4. Briefly explain why this song outweighs the others in urgency or severity.
"""

print("Analyzing songs with Gemini 3 Flash...\n")

# 4. Execute the request with Google Search Grounding enabled
response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents=prompt,
    config=types.GenerateContentConfig(
        # Enables Google Search Grounding so Gemini can search if it hits an unknown song
        # tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2  # Low temperature keeps rankings consistent and analytical
    )
)

# 5. Output the result
print("=== ANALYSIS RESULTS ===")
print(response.text)