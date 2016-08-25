import pseudo_entropy
import fs_repo

REPO = fs_repo
ENTROPY = pseudo_entropy

def get_diceware_list():
    contents = REPO.get_diceware_file_contents()
    lines = contents.split('\n')
    def _reduce(obj, line):
        splits = line.split('\t')
        obj[splits[0]] = splits[1]
        return obj
    dictionary = reduce(_reduce, lines)
    return dictionary

def gen_diceware_key():
    results = ''
    for i in range(5):
        results += str(ENTROPY.randint(1,6))
    return results

def gen_password(num_words, diceware_list):
    results = ''
    first = True
    for i in range(num_words):
        key = gen_diceware_key()
        word = diceware_list[key]
        space = ' '
        if first:
            first = False
            space = ''
        results += space + word
    return results


def gen_passwords(count, num_words=4):
    results = []
    diceware_list = get_diceware_list()
    passwords = [gen_password(num_words, diceware_list) for i in range(count)]



