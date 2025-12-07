import google.generativeai as genai
import requests
import json

from keys import gemini_key, groq_key, openrouter_key

prompt = input("Enter your problem: ")
try:
    genai.configure(api_key=gemini_key)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
    gemini_result = gemini_model.generate_content(prompt).text
except Exception as e:
    gemini_result = f"Gemini ERROR → {str(e)}"

try:
    groq_url = "https://api.groq.com/openai/v1/chat/completions"
    groq_payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    groq_headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }
    groq_response = requests.post(groq_url, json=groq_payload, headers=groq_headers)

    if groq_response.status_code == 200:
        groq_text = groq_response.json()["choices"][0]["message"]["content"]
    else:
        groq_text = f"Groq API Error: {groq_response.status_code} - {groq_response.text}"
except Exception as e:
    groq_text = f"Groq ERROR → {str(e)}"

try:
    openrouter_url = "https://openrouter.ai/api/v1/chat/completions"

    openrouter_payload = {
        "model": "meta-llama/llama-3.1-8b-instruct",  
        "messages": [{"role": "user", "content": prompt}]
    }

    openrouter_headers = {
        "Authorization": f"Bearer {openrouter_key}",
        "Content-Type": "application/json",
        "Referer": "http://localhost",     
        "X-Title": "Multi LLM CLI Tool"
    }

    openrouter_response = requests.post(openrouter_url, json=openrouter_payload, headers=openrouter_headers)

    if openrouter_response.status_code == 200:
        openrouter_text = openrouter_response.json()["choices"][0]["message"]["content"]
    else:
        openrouter_text = f"OpenRouter API Error: {openrouter_response.status_code} - {openrouter_response.text}"

except Exception as e:
    openrouter_text = f"OpenRouter ERROR → {str(e)}"

final = f"""
======================
     MULTI-LLM OUTPUT
======================

GEMINI:
{gemini_result}

GROQ:
{groq_text}

OPENROUTER (Llama-3.1):
{openrouter_text}


"""

print(final)
