import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"GEMINI_API_KEY is set: {bool(api_key)}")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash')
        response = model.generate_content("Say hello")
        print("Success! AI Response:", response.text)
    except Exception as e:
        print("Error during AI generation:", str(e))
else:
    print("GEMINI_API_KEY is missing in .env file.")
