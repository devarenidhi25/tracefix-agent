import os


def apply_import_fix(file_path: str, import_line: str) -> dict:
    if not os.path.exists(file_path):
        return {"status": "error", "message": "File not found"}

    with open(file_path, "r") as f:
        lines = f.readlines()

    # Check if already present
    for line in lines:
        if import_line in line:
            return {"status": "skipped", "message": "Import already exists"}

    # Insert at top
    lines.insert(0, import_line + "\n")

    with open(file_path, "w") as f:
        f.writelines(lines)

    return {"status": "success", "message": f"Added import: {import_line}"}
