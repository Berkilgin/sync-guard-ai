import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Render ortamından API anahtarını güvenli bir şekilde alıyoruz
api_key = os.getenv("AIzaSyDRXvvDY9QKqzf3vZMtYNS44QGb3Bw0go8")

# Fonksiyonun parametrelerine 'username' ekliyoruz
def resolve_sync_conflict(base_text, user1_input, username):
    if not api_key:
        return {
            "resolved_text": user1_input, 
            "action_log": "SYSTEM ERROR: GEMINI_API_KEY is missing."
        }

    client = genai.Client(api_key=api_key)
    
    # Prompt'a kullanıcının ismini dahil edip, logda bunu kullanmasını emrediyoruz
    prompt = f"""
    You are 'Sync Guard AI', a real-time collaborative workspace moderator.
    Context: "{base_text}"
    New Input from user '{username}': "{user1_input}"
    
    Tasks:
    1. Resolve conflicts, fix syntax errors if it's code, and censor inappropriate words with '***'.
    2. Provide a short action log explaining what you changed. You MUST include the username '{username}' in the log (e.g., "{username} added a new function", "Fixed unclosed parenthesis in {username}'s code", "Censored inappropriate word from {username}").
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "resolved_text": {"type": "STRING"},
                        "action_log": {"type": "STRING"}
                    },
                    "required": ["resolved_text", "action_log"]
                }
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {
            "resolved_text": user1_input, 
            "action_log": f"AI Error from {username}'s input: {str(e)}"
        }