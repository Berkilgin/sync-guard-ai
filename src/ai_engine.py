import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("AIzaSyDRXvvDY9QKqzf3vZMtYNS44QGb3Bw0go8"))

def resolve_sync_conflict(base_text, user1_input, user2_input):
    prompt = f"""
    You are 'Sync Guard AI', a real-time collaborative workspace moderator.
    Context: "{base_text}"
    New Input: "{user1_input}"
    
    Tasks:
    1. Resolve conflicts, fix syntax errors if it's code, and censor inappropriate words with '***'.
    2. Provide a short, one-sentence action log explaining what you changed (e.g., "Fixed unclosed parenthesis", "Censored inappropriate word", or "Merged inputs"). If no major change, write "Synced successfully".

    OUTPUT FORMAT: You MUST return strictly a valid JSON object. Do NOT wrap it in markdown code blocks. 
    Example format:
    {{
        "resolved_text": "the final clean text here",
        "action_log": "short log message here"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            
        return json.loads(raw_text)
    except Exception as e:
        return {
            "resolved_text": user1_input, 
            "action_log": f"Sync without AI intervention (API Error or timeout)."
        }