import multiprocessing as mp
from collections import Counter

counters = Counter()
validity = {}

def counters_num():
    # print("counters_num")
    counters["a"] += 1
    # print(counters["a"])

def for_test(num):
    print("num",num)
    print("for_test")
    for i in range(1000):
        counters_num()


if __name__ == "__main__":
    pool = mp.Pool(processes=int(5))
    result = pool.map(for_test, range(100))
    print(counters["a"])



