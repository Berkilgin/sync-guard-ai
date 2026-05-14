import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# dotenv ile gizli .env kasasını açıyoruz
load_dotenv()

# Şifreyi çevre değişkenlerinden (kasadan) çekiyoruz
api_key = os.getenv("GEMINI_API_KEY")

def resolve_sync_conflict(base_text, user1_input, username):
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are 'Sync Guard AI', a Python code moderator for a real-time workspace.
    
    Here is the current full code submitted by user '{username}':
    {user1_input}
    
    Tasks:
    1. Fix any syntax errors, typos (like 'printt' to 'print'), or logical conflicts.
    2. Censor inappropriate words with '***'.
    3. CRITICAL: You MUST preserve all Python indentation and line breaks (\\n). DO NOT squash the code into a single line. Return the properly formatted Python code exactly as a script should look.
    4. Provide a short action log including the username.
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
            "action_log": f"AI Hatası ({username}): {str(e)}"
        }