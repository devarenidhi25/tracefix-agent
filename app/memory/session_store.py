session_memory = {}


def get_session(session_id: str):
    return session_memory.get(session_id, [])


def add_to_session(session_id: str, entry: dict):
    if session_id not in session_memory:
        session_memory[session_id] = []

    session_memory[session_id].append(entry)
