import requests


def query_ollama(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        return "LLM request failed"

def llm_debug_analysis(error_trace: str) -> dict:
    prompt = f"""
You are a debugging assistant.

Analyze the following error and provide:

1. Root cause
2. Suggested fixes (list)

Error:
{error_trace}

Respond in this format:
Cause: ...
Fixes:
- ...
- ...
"""

    response = query_ollama(prompt)

    # very basic parsing
    cause = "LLM could not determine cause"
    fixes = []

    if "Cause:" in response:
        parts = response.split("Fixes:")
        cause = parts[0].replace("Cause:", "").strip()

        if len(parts) > 1:
            fixes = [f.strip("- ").strip() for f in parts[1].split("\n") if f.strip()]

    return {
        "cause": cause,
        "fixes": fixes
    }
