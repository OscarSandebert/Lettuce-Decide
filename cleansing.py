from openai import OpenAI, RateLimitError
import os

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

def correct_ingredient(user_input):

    prompt = f"""
Du får en lista med ingrediensnamn med eventuell felstavning.
Listan kan också innehålla andra formuleringar som inte är ingredienser — dessa ska tas bort.

Rätta stavningen.

Svara ENDAST med ingrediensernas namn, separerade med kommatecken.
Ingen förklaring.

Input: {user_input}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return [ingredient.strip().lower() for ingredient in response.choices[0].message.content.strip().split(',')]
    except RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        # Return a dictionary so the frontend or API route can detect the failure state
        return {"error": "RATE_LIMIT_REACHED"}