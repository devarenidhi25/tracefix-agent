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


def llm_debug_analysis(history: list, current_error: str) -> dict:
    prompt = f"""
You are a strict debugging assistant.

Analyze the error using previous debugging context.

IMPORTANT RULES:
- Do NOT guess advanced issues like cyclic dependency unless clearly indicated
- Focus on common developer mistakes first
- Be concise and accurate
- Output ONLY in the format below

Previous Errors:
{history}

Current Error:
{current_error}

Respond EXACTLY like this:

Cause: <short clear reason>

Fixes:
- <fix 1>
- <fix 2>
- <fix 3>
"""

    response = query_ollama(prompt)

    cause = "LLM could not determine cause"
    fixes = []

    try:
        if "Cause:" in response:
            cause_part = response.split("Cause:")[1]

            if "Fixes:" in cause_part:
                cause_text, fixes_part = cause_part.split("Fixes:")
                cause = cause_text.strip()

                fixes = [
                    line.strip("- ").strip()
                    for line in fixes_part.split("\n")
                    if line.strip().startswith("-")
                ]
            else:
                cause = cause_part.strip()

    except Exception:
        pass

    if not fixes:
        fixes = ["No reliable fixes generated. Try checking logs or environment."]

    return {
        "cause": cause,
        "fixes": fixes
    }
