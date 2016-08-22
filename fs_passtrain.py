import os

SESSION_DIR = 'sessions'
CACHE_FILEPATH = 'cache.json'

def build_session_filepath(session_id):
    return os.path.join(SESSION_DIR, "%d.json" % session_id)

def write(session, serialized_session):
    with open(build_session_filepath(session.id), 'w') as fin:
        fin.write(serialized_session)

def read(session_id):
    with open(build_session_filepath(session_id), 'r') as fout:
        string_session = fout.read()
        return string_session

def get_cache():
    with open(CACHE_FILEPATH, 'r') as fin:
        return fin.read()

def save_cache(serialized_cache):
    with open(CACHE_FILEPATH, 'w') as fout:
        fout.write(serialized_cache)
