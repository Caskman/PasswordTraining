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
        return str({
            "id": self.id,
            "password": self.password,
        })
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
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return str({
            "id_a": self.id_a,
            "id_b": self.id_b,
            "result": self.result,
            "in_cache": self.in_cache,
        })
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
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return str({
            "id": self.id,
            "passwords": [str(p) for p in self.passwords],
            "comparisons": [str(c) for c in self.comparisons],
        })
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
        return str({
            "level": self.level,
            "elements": [str(e) for e in self.elements],
        })
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
    serialized_cache = json.dumps(cache.cache, indent=4)
    SESSION_REPO.save_cache(serialized_cache)

def init_cache():
    cache = Cache({})
    save_cache(cache)

def gen_passwords(num):
    return [Password(i + 1, random.randint(0,10000)) for i in range(num)]

def generate_random_id():
    return random.randint(1, 1000000)

def create_fake_number_session(num=128):
    passwords = gen_passwords(num)
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
INTERMEDIATE_STATE_MODE = "INTERMEDIATE_STATE_MODE"
modes = [
    GET_NEXT_MODE,
    VALIDATE_NEXT_COMPARISON_MODE,
    INTERMEDIATE_STATE_MODE,
]

"""takes a string mode, session object, and an optional comparison object
if in get next mode, will return the next comparison object or the final array if 
all necessary comparisons exist in the session
if in comparison validation mode, will return a boolean indicating whether 
the test comparison object is a valid next comparison object for the session"""
def main_algorithm(mode, session, test_comparison_object=None):
    if mode not in modes:
        raise Exception("The fuck is this mode???")
    if session == None:
        raise Exception("Dude where's my session object?")
    if mode == VALIDATE_NEXT_COMPARISON_MODE and test_comparison_object == None:
        raise Exception("Dude where's my comparison object?")

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
        # print '=' * 50
        # print 'Subarrays'
        # print '=' * 50
        # print str(subarrays)
        # find the next pair of equal level subarrays to merge
        pair = get_next_subarray_pair(subarrays)
        # unpack the subarrays
        subarray1 = pair[0]
        subarray2 = pair[1]
        # this will be the new subarray that the two subarrays will be merged into
        new_subarray = Subarray([], subarray1.level + 1)
        # grab the first element of each subarray
        p1 = subarray1.peek()
        p2 = subarray2.peek()
        # keep merging until we've either found the next comparison to be made
        # or until one of the two subarrays is empty
        while comparison == None and not subarray1.isempty() and not subarray2.isempty():
            # alg_status = ''
            # push the winning password onto the new 
            # subarray and pull the next one off of its subarray
            def forward(result):
                if result < 0:
                    # alg_status += 'p1 is better; '
                    new_subarray.elements.append(subarray1.pop())
                    p1 = subarray1.peek_without_consequences()
                elif result > 0:
                    # alg_status += 'p2 is better; '
                    new_subarray.elements.append(subarray2.pop())
                    p2 = subarray2.peek_without_consequences()
                else:
                    raise Exception("Why the fuck is this comparison object's result shit?!?!?!")
            # if there's still comparisons left, apply them to the sort until there's no more
            if len(comps) > 0: 
                # alg_status += 'Comps left; '
                # get the next comparison to execute
                comp = comps.pop(0)
                # verify that the comparison matches the next passwords that need to be compared
                if comp.id_a != p1.id or comp.id_b != p2.id:
                    raise Exception("Your data is fucked up! Comparison doesn't match current state!")
                # ensure that the cache has this comparison
                cache.set(p1.password, p2.password, comp.result)
                # move the sorting along
                forward(comp.result)
            # at this point we executed all available comparisons
            # if we're in comparison validation mode, return whether or not the 
            # test comparison object is a valid next comparison object
            elif mode == VALIDATE_NEXT_COMPARISON_MODE:
                # alg_status += 'validating; '
                c = test_comparison_object
                return c.id_a == p1.id and c.id_b == p2.id
            # since there's no comparisons left, let's try the cache to see if 
            # we can get lucky and execute some comparisons stored in there
            else:
                # alg_status += 'No comps left/not validating; '
                # if we get a cache hit, we execute the comparison 
                # and add it to the session's history of comparisons
                if cache.exists(p1.password, p2.password):
                    # alg_status += 'cache hit; '
                    result = cache.get(p1.password, p2.password)
                    forward(result)
                    cache_comparison = Comparison(p1.id, p2.id, result, True)
                    session.comparisons.append(cache_comparison)
                # with no cache hit, we have our next 
                # comparison that needs to be resolved
                else:
                    # alg_status += 'cache miss; comparison generated; '
                    comparison = Comparison(p1.id, p2.id, None, False)
            # print alg_status
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

def standard_num_comp(p1, p2):
    return p1.password - p2.password

def test_main_algorithm(session=None, comparator=standard_num_comp):
    if session == None:
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
    print [str(e.password) for e in next.elements]
    prev = None
    for i in next.elements:
        if prev != None:
            # print i
            if prev.password > i.password:
                raise Exception("Fuck man... 1: %s 2: %s" % (str(prev), str(i)))
        prev = i

    print len(session.comparisons)
    cache_hits = [c for c in session.comparisons if c.in_cache == True]
    print "Cache hits: %d" % len(cache_hits)
    return session


if __name__ == '__main__':

    session = get_session(744876)
    # session.comparisons = []
    session = test_main_algorithm(session)

    # session = create_fake_number_session(8)
    # save_session(session)
    # print session.id

    # init_cache()
    # print session
    # save_session(session)

    # session_id = 81183
    # session = get_session(session_id)
    # save_session(session)


    # session = create_fake_number_session()
    # save_session(session)





