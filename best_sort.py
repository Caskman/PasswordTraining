import random
import heapq


def bubble_sort(items):
    """ Implementation of bubble sort """
    for i in range(len(items)):
        for j in range(len(items)-1-i):
            if items[j] > items[j+1]:
                items[j], items[j+1] = items[j+1], items[j]     # Swap!
def insertion_sort(items):
    """ Implementation of insertion sort """
    for i in range(1, len(items)):
        j = i
        while j > 0 and items[j] < items[j-1]:
            items[j], items[j-1] = items[j-1], items[j]
            j -= 1
def merge_sort(items):
    """ Implementation of mergesort """
    if len(items) > 1:
 
        mid = len(items) / 2    # Determine the midpoint and split
        left = items[0:mid]
        right = items[mid:]
 
        merge_sort(left)        # Sort left list in-place
        merge_sort(right)       # Sort right list in-place
 
        l, r = 0, 0
        for i in range(len(items)):     # Merging the left and right list
 
            lval = left[l] if l < len(left) else None
            rval = right[r] if r < len(right) else None
 
            if (lval and rval and lval < rval) or rval is None:
                items[i] = lval
                l += 1
            elif (lval and rval and lval >= rval) or lval is None:
                items[i] = rval
                r += 1
            else:
                raise Exception('Could not merge, sub arrays sizes do not match the main array')
def quick_sort(items):
    """ Implementation of quick sort """
    if len(items) > 1:
        pivot_index = len(items) / 2
        smaller_items = []
        larger_items = []
 
        for i, val in enumerate(items):
            if i != pivot_index:
                if val < items[pivot_index]:
                    smaller_items.append(val)
                else:
                    larger_items.append(val)
 
        quick_sort(smaller_items)
        quick_sort(larger_items)
        items[:] = smaller_items + [items[pivot_index]] + larger_items
 
def heap_sort(items):
    """ Implementation of heap sort """
    heapq.heapify(items)
    items[:] = [heapq.heappop(items) for i in range(len(items))]

def shell_sort(alist):
    sublistcount = len(alist)//2
    while sublistcount > 0:

        for startposition in range(sublistcount):
            gapInsertionSort(alist,startposition,sublistcount)

        sublistcount = sublistcount // 2

def gapInsertionSort(alist,start,gap):
    for i in range(start+gap,len(alist),gap):

        currentvalue = alist[i]
        position = i

        while position>=gap and alist[position-gap]>currentvalue:
            alist[position]=alist[position-gap]
            position = position-gap

        alist[position]=currentvalue


class Counter():
    def __init__(self):
        self.c = 0
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return str(self.c)
    def up(self):
        self.c += 1
    def reset(self):
        self.c = 0
    def count(self):
        return self.c
class MyNumber():
    def __init__(self, n, counter, cache):
        self.counter = counter
        self.n = n
        self.cache = cache
        if (self.cache == None):
            print 'Ugh' ,
    def __cmp__(self, other):
        if not self.cache.exists(self.n, other.n):
            self.cache.set(self.n, other.n)
            self.counter.up()
        return self.n - other.n
    def __repr__(self):     
        return self.__str__()
    def __str__(self):
        return str(self.n)
class Sort():
    def __init__(self, name, sort, cache):
        self.name = name
        self.sort = sort
        self.counter = Counter()
        self.cache = cache
        self.counts = []
    def go(self, items):
        self.counter.reset()
        new_list = [MyNumber(i, self.counter, self.cache) for i in items]
        self.sort(new_list)
    def report(self):
        print "%s has %d comparisons" % (self.name, self.counter.count())
    def count(self):
        return self.counter.count()
    def store(self):
        self.counts.append(self.count())
    def reset(self):
        self.counts = []
        self.counter.reset()

class NumCache():
    def __init__(self, disable):
        self.cache = {}
        self.disable = disable
    def exists(self, a, b):
        if self.disable == True:
            return False
        return (a, b) in self.cache
    def set(self, a, b):
        self.cache[(a, b)] = True
        self.cache[(b, a)] = False
    def reset(self):
        self.cache = {}

def run(sorts, cache, n_list):
    for s in sorts:
        s.reset()

    for sort_f in sorts:
        counter = Counter()
        cache.reset()
        sort_f.go(n_list)

    for s in sorted(sorts, lambda a, b: a.count() - b.count()):
        s.report()

def shuffle(n_list):
    num_shuffles = 1000
    length = 5
    new_list = [i for i in n_list]
    for i in range(num_shuffles):
        start_index = random.randint(0, (len(n_list) - length))
        chunk = new_list[start_index: start_index + length]
        random.shuffle(chunk)
        new_list[start_index: start_index + length] = chunk
    return new_list

def main():
    cache = NumCache(True)
    sorts = [
        Sort('Bubble', bubble_sort, cache),
        Sort('Insertion', insertion_sort, cache),
        Sort('Merge', merge_sort, cache),
        Sort('Quick', quick_sort, cache),
        Sort('Heap', heap_sort, cache),
        Sort('Shell', shell_sort, cache),
    ]

    original_list = [random.randint(0, 1000000) for c in range(100)]
    sorted_list = sorted(original_list)
    shuffled_list = shuffle(sorted_list)

    print "Sorted"
    run(sorts, cache, sorted_list)

    print "Nearly Sorted"
    run(sorts, cache, shuffled_list)

    print "Random"
    run(sorts, cache, original_list)

if __name__ == '__main__':
    main()


