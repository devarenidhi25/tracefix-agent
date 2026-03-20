import re


def detect_language(error_trace: str) -> str:
    if "Traceback" in error_trace:
        return "Python"
    if "Exception in thread" in error_trace:
        return "Java"
    if "npm ERR" in error_trace:
        return "Node.js"
    return "Unknown"


def classify_error(error_trace: str) -> str:
    if "ModuleNotFoundError" in error_trace:
        return "Missing Dependency"
    if "ImportError" in error_trace:
        return "Import Error"
    if "SyntaxError" in error_trace:
        return "Syntax Error"
    if "TypeError" in error_trace:
        return "Type Error"
    return "Unknown"


def extract_module(error_trace: str) -> str:
    match = re.search(r"No module named '(.+?)'", error_trace)
    if match:
        return match.group(1)
    return ""


def parse_error(error_trace: str) -> dict:
    return {
        "language": detect_language(error_trace),
        "error_type": classify_error(error_trace),
        "module": extract_module(error_trace),
    }
