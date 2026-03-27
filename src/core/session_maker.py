import uuid
from threading import Event
active_session = {}

def create_session():
    session_id = str(uuid.uuid4())
    active_session[session_id] = {
        "threads":[],
        "queue":None,
        "match_queue":None,
        "id":session_id,
        "stop_event":Event()
    }
    return active_session[session_id]


def stop_session(session_id):
    session = active_session.get(session_id,None)
    if session:
        session["stop_event"].set()
        return True
    return False

def get_session(session_id:str):
    return active_session[session_id]

def delete_session(session_id:str):
    return active_session.pop(session_id,None)

def get_active_sessions():
    return [k for k in active_session.keys()]