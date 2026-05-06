from google import genai
import os

# Sätt din API-nyckel här eller via environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=GEMINI_API_KEY)

def correct_ingredient(user_input):

    prompt = f"""
Du får en lista med ingrediensnamn med eventuell felstavning.
Listan kan också innehålla andra formuleringar som inte är ingredienser — dessa ska tas bort.

Rätta stavningen.

Svara ENDAST med ingrediensernas namn, separerade med kommatecken.
Ingen förklaring.

Input: {user_input}
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
        config={
            "temperature": 0
        }
    ) 

    return [ingredient.strip().lower() for ingredient in response.text.strip().split(',')]