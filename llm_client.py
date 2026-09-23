import os
import requests 
import ollama
import google.generativeai as genai
from dotenv import load_dotenv



load_dotenv()

genai.configure(api_key=os.getenv("Gemini_API_KEY"))

HF_API_KEY=os.getenv("HF_API_KEY")
HF_HEADERS={"Authorization": f"Bearer {HF_API_KEY}"}


def call_gemini(prompt, model, temperature, max_tokens):
    llm=genai.GenerativeModel(model)
    response= llm.generate_content(
        prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens":max_tokens
        }
    )
    return response.text


def call_hf(prompt, model, temperature, max_tokens):
    # Mistral & chat models → new HF Chat API
    if "mistral" in model.lower():
        url = "https://api-inference.huggingface.co/v1/chat/completions"

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            url,
            headers=HF_HEADERS,
            json=payload,
            timeout=90
        )
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    # Legacy text-generation models (FLAN, etc.)
    else:
        url = f"https://api-inference.huggingface.co/models/{model}"

        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens
            }
        }

        response = requests.post(
            url,
            headers=HF_HEADERS,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        return response.json()[0]["generated_text"]



def call_ollama(prompt, model, temperature, max_tokens):
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        options={
            "temperature": temperature,
            "num_predict": max_tokens
        }
    )
    return response["message"]["content"]


def call_llm(prompt, model_cfg, temperature, max_tokens):
    provider=model_cfg["provider"]
    model=model_cfg["model"]

    if provider == "gemini":
        return call_gemini(prompt, model, temperature, max_tokens)
    
    if provider == "huggingface":
        return call_hf(prompt, model, temperature, max_tokens)
    
    if provider == "ollama":
        return call_ollama(prompt, model, temperature, max_tokens)
    
    raise ValueError("Unsupprted LLM Model")





