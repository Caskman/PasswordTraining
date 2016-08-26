import random
import json
import os
import fs_repo
import diceware

REPO = fs_repo

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
            d["password"],
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
    def __init__(self, cache, disabled):
        self.cache = cache
        self.disabled = disabled
    def get_comparison_string(self, password_a, password_b):
        return "%s < %s" % (str(password_a), str(password_b))
    def exists(self, password_a, password_b):
        if self.disabled:
            return False
        return self.get_comparison_string(password_a, password_b) in self.cache
    def get(self, password_a, password_b):
        if self.disabled:
            return None
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

def get_cache(disabled=False):
    serialized_cache = REPO.get_cache()
    cache = json.loads(serialized_cache)
    return Cache(cache, disabled)

def save_cache(cache):
    if not cache.disabled:
        serialized_cache = json.dumps(cache.cache, indent=4)
        REPO.save_cache(serialized_cache)

def init_cache():
    cache = Cache({})
    save_cache(cache)

def gen_passwords(num):
    return [Password(i + 1, random.randint(0,10000)) for i in range(num)]

def generate_random_id():
    return random.randint(1, 1000000)

def create_fake_number_session(num=128):
    passwords = [Password(i + 1, v) for i, v in enumerate(gen_passwords(num))]
    comparisons = []
    return Session(generate_random_id(), passwords, comparisons)

def get_next_subarray_pair(subarrays):
    for i in range(len(subarrays) - 1):
        curr = subarrays[i]
        next = subarrays[i + 1]
        if curr.level == next.level:
            return (curr, next)


def flatten_subarrays(subarrays):
    passwords = []
    for subarray in subarrays:
        passwords.extend(subarray.elements)
    return passwords

special_log_status = '=' * 30
def log_status(msg):
    special_log_status += msg


def dump_log_status():
    global special_log_status
    print special_log_status
    special_log_status = '=' * 30


def stringify_subarray(subarray):
    nums = map(lambda x: x.password, subarray.elements)
    str_result = ''
    first = True
    for n in nums:
        comma = ', '
        if first:
            comma = ''
            first = False
        str_result += comma + str(n)
    return '|%s|' % str_result

def output_session(subarrays, subarray1, subarray2, new_subarray):
    print '=' * 40
    print 'Sub Arrays'
    str_subarrays = map(stringify_subarray, subarrays)
    result = ''
    first = True
    for s in str_subarrays:
        space = ' '
        if first:
            first = False
            space = ''
        result += space + s
    print '\t' + result

    print 'Working Subarrays'
    s1 = stringify_subarray(subarray1)
    s2 = stringify_subarray(subarray2)
    print '\tS1: %s === S2: %s' % (s1, s2)

    print 'New Subarray'
    print '\t' + stringify_subarray(new_subarray)

SINGLETON_LOG_MSG = ''
def init_log():
    SINGLETON_LOG_MSG = '=' * 30
init_log()

def log_to_singleton(msg):
    global SINGLETON_LOG_MSG
    SINGLETON_LOG_MSG += msg + '\n'

def dump_singleton_log():
    print SINGLETON_LOG_MSG
    init_log()

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
def main_algorithm(mode, session, test_comparison_object=None, verbose=False, log_everything=False):
    if mode not in modes:
        raise Exception("The fuck is this mode???")
    if session == None:
        raise Exception("Dude where's my session object?")
    if mode == VALIDATE_NEXT_COMPARISON_MODE and test_comparison_object == None:
        raise Exception("Dude where's my comparison object?")

    init_log()
    def log_it(msg):
        if log_everything:
            log_to_singleton(msg + '\n')

    def dump_log():
        if log_everything:
            dump_singleton_log()

    log_it('Mode: %s' % mode)

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
        new_subarray = Subarray([], subarray1.level + 1)
        # grab the first element of each subarray
        p1 = subarray1.peek()
        p2 = subarray2.peek()
        log_it('Beginning another merge')
        log_it('S1: %s S2: %s' % (stringify_subarray(subarray1), stringify_subarray(subarray2)))
        log_it('p1: %s p2: %s' % (str(p1.password), str(p2.password)))
        # keep merging until we've either found the next comparison to be made
        # or until one of the two subarrays is empty
        while comparison == None and not subarray1.isempty() and not subarray2.isempty():
            if verbose:
                print 'Main Algo Verbose'
                output_session(subarrays, subarray1, subarray2, new_subarray)
            log_it('Comparing %s %s' % (str(p1.password), str(p2.password)))
            log_it('Comps Length: %d' % len(comps))
            # push the winning password onto the new 
            # subarray and pull the next one off of its subarray
            def forward(result):
                log_it('Result is %s' % str(result))
                new_p1 = p1
                new_p2 = p2
                if result < 0:
                    log_it('p1 is better')
                    # log_status('p1 is better; ')
                    new_subarray.elements.append(subarray1.pop())
                    new_p1 = subarray1.peek_without_consequences()
                elif result > 0:
                    log_it('p2 is better')
                    # log_status('p2 is better; ')
                    new_subarray.elements.append(subarray2.pop())
                    new_p2 = subarray2.peek_without_consequences()
                else:
                    raise Exception("Why the fuck is this comparison object's result shit?!?!?!")
                return (new_p1, new_p2)
            # if there's still comparisons left, apply them to the sort until there's no more
            if len(comps) > 0:
                log_it('Executing Comparison')
                # log_status('Comps left; ')
                # get the next comparison to execute
                comp = comps.pop(0)
                # verify that the comparison matches the next passwords that need to be compared
                if comp.id_a != p1.id or comp.id_b != p2.id:
                    raise Exception("Your data is fucked up! Comparison doesn't match current state!")
                # ensure that the cache has this comparison
                cache.set(p1.password, p2.password, comp.result)
                # move the sorting along
                new_ps = forward(comp.result)
                p1 = new_ps[0]
                p2 = new_ps[1]
            # at this point we executed all available comparisons
            # if we're in comparison validation mode, return whether or not the 
            # test comparison object is a valid next comparison object
            elif mode == VALIDATE_NEXT_COMPARISON_MODE:
                log_it('Validation')
                c = test_comparison_object
                dump_log()
                return c.id_a == p1.id and c.id_b == p2.id
            # in intermediate state mode, we want to return the status of the sorting by
            # returning the array itself in its current state, regardless if it's sorted or not
            elif mode == INTERMEDIATE_STATE_MODE:
                log_it('Outputting Session')
                output_session(subarrays, subarray1, subarray2, new_subarray)
                dump_log()
                return None
            # since there's no comparisons left, let's try the cache to see if 
            # we can get lucky and execute some comparisons stored in there
            else:
                log_it('Checking cache')
                # if we get a cache hit, we execute the comparison 
                # and add it to the session's history of comparisons
                if cache.exists(p1.password, p2.password):
                    log_it('Cache hit')
                    result = cache.get(p1.password, p2.password)
                    cache_comparison = Comparison(p1.id, p2.id, result, True)
                    session.comparisons.append(cache_comparison)
                    new_ps = forward(result)
                    p1 = new_ps[0]
                    p2 = new_ps[1]
                # with no cache hit, we have our next 
                # comparison that needs to be resolved
                else:
                    log_it('Cache Miss')
                    comparison = Comparison(p1.id, p2.id, None, False)
        dump_log()
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
        return subarrays[0].elements
    else:
        raise Exception("Why are you not returning anything?! Fuck!!!")

# ================================================================================
# Public Functions
# ================================================================================

def setup():
    if not os.path.isfile('cache.json'):
        with open('cache.json', 'w') as fout:
            fout.write('{}')
    if not os.path.isdir('sessions'):
        os.mkdir('sessions')

def create_comparison(session, password1, password2, result):
    id_a = filter(lambda x: x.password == password1,session.passwords)[0].id
    id_b = filter(lambda x: x.password == password2,session.passwords)[0].id
    return Comparison(id_a, id_b, result, False)

def create_session():
    passwords = [Password(i + 1, p) for i, p in enumerate(diceware.gen_passwords(32))]
    comparisons = []
    session = Session(generate_random_id(), passwords, comparisons)
    return session

def save_session(session):
    dict_session = session.encode()
    REPO.write(session, json.dumps(dict_session, indent=4))

def get_session(id):
    serialized_session = REPO.read(id)
    dict_session = json.loads(serialized_session)
    session = Session.decode(dict_session)
    return session

def get_next_comparison(session, verbose=False):
    return main_algorithm(GET_NEXT_MODE, session, verbose=verbose)

def validate_next_comparison(session, comparison):
    return main_algorithm(VALIDATE_NEXT_COMPARISON_MODE, session, comparison)

def commit_next_comparison(session, comparison):
    if validate_next_comparison(session, comparison):
        session.comparisons.append(comparison)
        save_session(session)
        return True
    else:
        return False

def list_sessions():
    return REPO.list_sessions()

# ================================================================================
# Test Functions
# ================================================================================

def standard_num_comp(p1, p2):
    return p1.password - p2.password

def output_intermediate_state(session):
    print 'Outputting Intermediate State'
    main_algorithm(INTERMEDIATE_STATE_MODE, session, log_everything=True)

def test_main_algorithm(session=None, comparator=standard_num_comp, verbose=False):
    if session == None:
        session = create_fake_number_session()
    next = get_next_comparison(session)
    while isinstance(next, Comparison):
        if verbose:
            output_intermediate_state(session)
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

    setup()
    # print get_session(458222)

    # print REPO.list_sessions()

    # session = create_fake_number_session(32)
    # session = get_session(795642)
    # session = test_main_algorithm(session, verbose=False)

    # import os
    # print 'Working Dir'
    # print os.getcwd()

    # session.comparisons = []
    # output_intermediate_state(session)

    # 795642

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
