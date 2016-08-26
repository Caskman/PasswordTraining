import os
from os import listdir
from os.path import isfile, join

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

def get_diceware_file_contents():
    with open('alternate-diceware-list.txt', 'r') as fin:
        return fin.read()

def list_sessions():
    files = [f for f in listdir(SESSION_DIR) if isfile(join(SESSION_DIR, f))]
    return map(lambda f: f.replace('.json', ''), files)
