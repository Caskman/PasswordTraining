import random
import json
import os
import fs_sessions

SESSION_REPO = fs_sessions

#=============================================
# Persistent Entities
#=============================================

class Password():
    def __init__(self, id, password):
        self.id = id # integer
        self.password = password # integer for now
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return str(self.password)
    def encode(self):
        return {
            "id": self.id,
            "password": self.password,
        }
    @staticmethod
    def decode(d):
        return Password(
            int(d["id"]),
            int(d["password"]),
        )

class Comparison():
    def __init__(self, id_a, id_b, result, in_cache):
        self.id_a = id_a # integer id pointing to a password
        self.id_b = id_b # integer id pointing to a password
        self.result = result # integer where -1 means id_a < id_b and so on and so forth
        self.in_cache = in_cache # boolean indicating whether this comparison was already in the cache
    def encode(self):
        return {
            "id_a": self.id_a,
            "id_b": self.id_b,
            "result": self.result,
            "in_cache": self.in_cache,
        }
    @staticmethod
    def decode(d):
        return Comparison(
            int(d["id_a"]),
            int(d["id_b"]),
            int(d["result"]),
            bool(d["in_cache"]),
        )
    def has_result(self):
        return self.result != None

class Session():
    def __init__(self, id, passwords, comparisons):
        self.id = id # integer id
        self.passwords = passwords # list of Password objects
        self.comparisons = comparisons # list of Comparison objects
    def encode(self):
        return {
            "id": self.id,
            "passwords": [password.encode() for password in self.passwords],
            "comparisons": [comparison.encode() for comparison in self.comparisons],
        }
    @staticmethod
    def decode(d):
        return Session(
            int(d["id"]),
            [Password.decode(password) for password in d["passwords"]],
            [Comparison.decode(comparison) for comparison in d["comparisons"]],
        )

class Cache():
    def __init__(self, cache):
        self.cache = cache
    def get_comparison_string(self, password_a, password_b):
        return "%s < %s" % (str(password_a), str(password_b))
    def exists(self, password_a, password_b):
        return self.get_comparison_string(password_a, password_b) in self.cache
    def get(self, password_a, password_b):
        return self.cache[self.get_comparison_string(password_a, password_b)]
    def set(self, password_a, password_b, val):
        key = self.get_comparison_string(password_a, password_b)
        self.cache[key] = val
        key = self.get_comparison_string(password_b, password_a)
        self.cache[key] = val * -1


#============================================================
# Volatile Entities
#============================================================

class Subarray():
    def __init__(self, elements, level):
        self.elements = elements
        self.level = level
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return str(self.elements)
    def isempty(self):
        return len(self.elements) == 0
    def peek(self):
        return self.elements[0]
    def peek_without_consequences(self):
        if len(self.elements) > 0:
            return self.peek()
        else:
            return None
    def pop(self):
        e = self.elements[0]
        self.elements = self.elements[1:]
        return e


#============================================================
# Functions
#============================================================

def get_cache():
    serialized_cache = SESSION_REPO.get_cache()
    cache = json.loads(serialized_cache)
    return Cache(cache)

def save_cache(cache):
    serialized_cache = json.dumps(cache.cache)
    SESSION_REPO.save_cache(serialized_cache)

def init_cache():
    cache = Cache({})
    save_cache(cache)

def gen_passwords(num):
    return [Password(i + 1, random.randint(0,10000)) for i in range(num)]

def generate_random_id():
    return random.randint(1, 1000000)

def create_fake_number_session():
    passwords = gen_passwords(10)
    comparisons = []
    return Session(generate_random_id(), passwords, comparisons)

def save_session(session):
    dict_session = session.encode()
    SESSION_REPO.write(session, json.dumps(dict_session, indent=4))

def get_session(id):
    serialized_session = SESSION_REPO.read(id)
    dict_session = json.loads(serialized_session)
    session = Session.decode(dict_session)
    return session

def get_next_subarray_pair(subarrays):
    for i in range(len(subarrays) - 1):
        curr = subarrays[i]
        next = subarrays[i + 1]
        if curr.level == next.level:
            return (curr, next)

GET_NEXT_MODE = "GET_NEXT"
VALIDATE_NEXT_COMPARISON_MODE = "VALIDATE_NEXT_COMPARISON"

"""takes a string mode, session object, and an optional comparison object
if in get next mode, will return the next comparison object or the final array if 
all necessary comparisons exist in the session
if in comparison validation mode, will return a boolean indicating whether 
the test comparison object is a valid next comparison object for the session"""
def main_algorithm(mode, session, test_comparison_object=None):
    if mode == GET_NEXT_MODE:
        if session == None:
            raise Exception("Dude where's my session object?")
    elif mode == VALIDATE_NEXT_COMPARISON_MODE:
        if session == None:
            raise Exception("Dude where's my session object?")
        if test_comparison_object == None:
            raise Exception("Dude where's my comparison object?")
    else:
        raise Exception("The fuck is this mode???")

    # acquire cache object for skipping unnecessary comparisons
    cache = get_cache()
    # convert all passwords into length 1 subarrays to begin merge sort
    subarrays = [Subarray([password], 1) for password in session.passwords]
    # copy the comparisons array so we can whittle down the list of comparisons
    comps = [c for c in session.comparisons]

    # the eventual comparison object to be returned
    comparison = None
    # continue sorting until we've found the next comparison that the user needs to give us
    # or until we've whittled it all down to the final array
    while comparison == None and len(subarrays) > 1:
        # find the next pair of equal level subarrays to merge
        pair = get_next_subarray_pair(subarrays)
        # unpack the subarrays
        subarray1 = pair[0]
        subarray2 = pair[1]
        # this will be the new subarray that the two subarrays will be merged into
        new_subarray = Subarray([], 2)
        # grab the first element of each subarray
        p1 = subarray1.peek()
        p2 = subarray2.peek()
        # keep merging until we've either found the next comparison to be made
        # or until one of the two subarrays is empty
        while comparison == None and not subarray1.isempty() and not subarray2.isempty():
            # if there's still comparisons left, apply them to the sort until there's no more
            if len(comps) > 0: 
                # get the next comparison to execute
                comp = comps.pop(0)
                # verify that the comparison matches the next passwords that need to be compared
                if comp.id_a != p1.id or comp.id_b != p2.id:
                    raise Exception("Your data is fucked up! Comparison doesn't match current state!")
                # push the winning password onto the new 
                # subarray and pull the next one off of its subarray
                if comp.result < 0:
                    new_subarray.elements.append(subarray1.pop())
                    p1 = subarray1.peek_without_consequences()
                elif comp.result > 0:
                    new_subarray.elements.append(subarray2.pop())
                    p2 = subarray2.peek_without_consequences()
                else:
                    raise Exception("Why the fuck is this comparison object's result shit?!?!?!")
            # at this point we executed all available comparisons
            # if we're in comparison validation mode, return whether or not the 
            # test comparison object is a valid next comparison object
            elif mode == VALIDATE_NEXT_COMPARISON_MODE:
                c = test_comparison_object
                return c.id_a == p1.id and c.id_b == p2.id
            # since there's no comparisons left, let's try the cache to see if 
            # we can get lucky and execute some comparisons stored in there
            else:
                # if we get a cache hit, we execute the comparison 
                # and add it to the session's history of comparisons
                if cache.exists(p1.password, p2.password):
                    result = cache.get(p1.password, p2.password)
                    cache_comparison = Comparison(p1.id, p2.id, result, True)
                    session.comparisons.append(cache_comparison)
                # with no cache hit, we have our next 
                # comparison that needs to be resolved
                else:
                    comparison = Comparison(p1.id, p2.id, None, False)
        # if the comparison wasn't found, that means we emptied one of the subarrays
        # two subarrays.  Now we need to empty the other subarray into the new subarray
        # and replace those two subarrays with the new subarray
        if comparison == None:
            if not subarray1.isempty():
                new_subarray.elements.extend(subarray1.elements)
            if not subarray2.isempty():
                new_subarray.elements.extend(subarray2.elements)
            subarrays[subarrays.index(subarray1)] = new_subarray
            subarrays.remove(subarray2)
    # save cache since we're all done with comparisons
    save_cache(cache)
    # since we found the next comparison object, return it
    if comparison != None:
        return comparison
    # Since we're now left with the final array, return the array
    elif len(subarrays) == 1:
        return subarrays[0]
    else:
        raise Exception("Why are you not returning anything?! Fuck!!!")

def get_next_comparison(session):
    return main_algorithm(GET_NEXT_MODE, session)

def validate_next_comparison(session, comparison):
    return main_algorithm(VALIDATE_NEXT_COMPARISON_MODE, session, comparison)

def commit_next_comparison(session, comparison):
    if validate_next_comparison(session, comparison):
        session.comparisons.append(comparison)
        save_session(session)
        return True
    else:
        return False

def test_main_algorithm():
    session = create_fake_number_session()
    next = get_next_comparison(session)
    while isinstance(next, Comparison):
        if isinstance(next.id_a, int) and isinstance(next.id_b, int):
            n1 = filter(lambda x: x.id == next.id_a, session.passwords)[0]
            n2 = filter(lambda x: x.id == next.id_b, session.passwords)[0]
            next.result = n1.password - n2.password
            if validate_next_comparison(session, next):
                session.comparisons.append(next)
            else:
                raise Exception("Goddammit! validation failed...")
        else:
            raise Exception("Fucking integers man...")
        next = get_next_comparison(session)
    print next


if __name__ == '__main__':

    # init_cache()
    test_main_algorithm()

    # session_id = 81183
    # session = get_session(session_id)
    # save_session(session)


    # session = create_fake_number_session()
    # save_session(session)





