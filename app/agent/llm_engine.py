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


def llm_debug_analysis(context: str, current_error: str) -> dict:
    prompt = f"""
You are a strict debugging assistant.

Analyze the error using previous debugging steps.

IMPORTANT RULES:
- Do NOT repeat fixes that were already suggested
- If previous fix did not work, suggest an alternative approach
- Use previous steps to refine the solution
- Focus on practical developer mistakes
- Be concise and accurate

Debugging Context:
{context}

Current Error:
{current_error}

Respond EXACTLY like this:

Cause: <short clear reason>

Fixes:
- <new fix 1>
- <new fix 2>
- <new fix 3>
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
                    line.strip("- ").strip("* ").strip()
                    for line in fixes_part.split("\n")
                    if line.strip().startswith(("-", "*"))
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
