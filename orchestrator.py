import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Initialize the model
try:
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    model = None

def build_system_prompt(user_profile: dict) -> str:
    """
    Builds the base system prompt with user profile context and required rules.
    """
    # Base persona and instruction
    sys_prompt = "You are FreelanceFlow PK, an AI assistant for Pakistani freelancers. Respond only in valid JSON.\n\n"
    sys_prompt += "Never ask for information already present in the user profile. Treat the profile as ground truth.\n\n"
    
    # Add User Profile Info
    sys_prompt += f"=== USER PROFILE ===\n"
    sys_prompt += f"Name: {user_profile.get('name')}\n"
    sys_prompt += f"Domain: {user_profile.get('domain')}\n"
    sys_prompt += f"Experience Level: {user_profile.get('experience_level')}\n"
    sys_prompt += f"Current Rate: ${user_profile.get('current_rate_usd')}/hr\n"
    sys_prompt += f"Target Platforms: {', '.join(user_profile.get('platforms', []))}\n"
    sys_prompt += f"Top Skills: {', '.join(user_profile.get('top_skills', []))}\n"
    sys_prompt += f"Language Preference: {user_profile.get('language_pref')}\n"
    
    # Adaptive Tone Based on Experience Level
    exp = user_profile.get('experience_level', '').lower()
    if exp in ['intermediate', 'expert']:
        sys_prompt += "Tone: Confident, professional, and authoritative.\n"
    else:
        sys_prompt += "Tone: Eager, credible, and professional but showing willingness to learn and adapt.\n"
        
    # Language Preference Rule
    if user_profile.get('language_pref', '').lower() == 'roman_urdu':
        sys_prompt += "IMPORTANT: Since language_pref is roman_urdu, all user-facing output (e.g., text, descriptions, explanations) MUST be in Roman Urdu. However, JSON keys MUST remain in English.\n"
        
    sys_prompt += "\n"
    return sys_prompt

def clean_json_response(text: str) -> str:
    """Strips markdown fences and cleans text to ensure JSON parsing."""
    clean = re.sub(r"```json|```", "", text).strip()
    return clean

def generate(user_profile: dict, task_prompt: str, context: str = "") -> dict:
    """
    Main orchestrator function to call Gemini with profile and context.
    Returns a parsed JSON dictionary.
    """
    if not model:
        return {"error": "Gemini model is not configured. Check GEMINI_API_KEY."}

    full_prompt = build_system_prompt(user_profile)
    
    if context:
        full_prompt += f"=== ADDITIONAL CONTEXT (Web Search/Data) ===\n{context}\n\n"
        
    full_prompt += f"=== TASK ===\n{task_prompt}\n"
    full_prompt += "Remember: Output MUST be ONLY valid JSON. No markdown formatting, no intro text, no backticks."

    try:
        response = model.generate_content(full_prompt)
        cleaned_text = clean_json_response(response.text)
        
        try:
            data = json.loads(cleaned_text)
            return data
        except json.JSONDecodeError as json_err:
            print(f"JSON Parsing Error: {json_err}")
            print(f"Raw response: {cleaned_text}")
            return {
                "error": "Failed to parse generated response into JSON.",
                "raw_response": cleaned_text
            }
            
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return {"error": str(e)}
