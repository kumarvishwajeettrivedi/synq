import google.generativeai as genai
import requests
import json
from keys import gemini_key, groq_key, openrouter_key

def query_gemini(prompt):
    try:
        genai.configure(api_key=gemini_key)
        gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        return gemini_model.generate_content(prompt).text
    except Exception as e:
        return f"Gemini ERROR → {str(e)}"

def query_groq(prompt):
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
            return groq_response.json()["choices"][0]["message"]["content"]
        else:
            return f"Groq API Error: {groq_response.status_code} - {groq_response.text}"
    except Exception as e:
        return f"Groq ERROR → {str(e)}"

def query_openrouter(prompt):
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
            return openrouter_response.json()["choices"][0]["message"]["content"]
        else:
            return f"OpenRouter API Error: {openrouter_response.status_code} - {openrouter_response.text}"
    except Exception as e:
        return f"OpenRouter ERROR → {str(e)}"
