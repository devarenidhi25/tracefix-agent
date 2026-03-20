def generate_reasoning(parsed_data: dict) -> dict:
    error_type = parsed_data.get("error_type")
    module = parsed_data.get("module")

    cause = "Unable to determine cause"
    fixes = []

    if error_type == "Missing Dependency":
        cause = f"The required module '{module}' is not installed in your environment."
        fixes = [
            f"Install the package using: pip install {module}",
            "Ensure you are using the correct virtual environment",
            "Check if the package name is correct"
        ]

    elif error_type == "Import Error":
        cause = "There is an issue with importing a module or function."
        fixes = [
            "Check module name and spelling",
            "Verify file structure and import paths"
        ]

    elif error_type == "Syntax Error":
        cause = "There is a syntax mistake in your code."
        fixes = [
            "Check for missing brackets or colons",
            "Review indentation and formatting"
        ]

    return {
        "cause": cause,
        "fixes": fixes
    }
