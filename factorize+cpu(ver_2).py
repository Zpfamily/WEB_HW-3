from time import time
import logging
import multiprocessing

logging.basicConfig(level=logging.INFO)

def factorize_single(num):
    start_time = time()
    factors = []
    for i in range(1, num + 1):
        if num % i == 0:
            factors.append(i)
    end_time = time()
    elapsed_time = end_time - start_time
    logging.info(f"Factorize for {num} took {elapsed_time:.6f} seconds.")
    return factors

def factorize_sync(*number):
    result = []
    for num in number:
        result.append(factorize_single(num))
    return tuple(result)

def factorize_multi(nums, pool):
    result = []
    for num in nums:
        result.append(pool.apply_async(factorize_single, (num,)).get())
    return tuple(result)

if __name__ == "__main__":
    # Test synchronous version
    start_time_sync = time()
    a, b, c, d = factorize_sync(128, 255, 99999, 10651060)
    logging.info(f"Synchronous factorization for all numbers took {time() - start_time_sync:.6f} seconds.")
    
    # Test multiprocessing version
    start_time_multi = time()
    num_cores = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_cores)
    a, b, c, d = factorize_multi([128, 255, 99999, 10651060], pool)
    logging.info(f"Multiprocessing factorization for all numbers took {time() - start_time_multi:.6f} seconds.")
    
    assert a == [1, 2, 4, 8, 16, 32, 64, 128]
    assert b == [1, 3, 5, 15, 17, 51, 85, 255]
    assert c == [1, 3, 9, 41, 123, 271, 369, 813, 2439, 11111, 33333, 99999]
    assert d == [1, 2, 4, 5, 7, 10, 14, 20, 28, 35, 70, 140, 76079, 152158, 304316, 380395, 532553, 760790, 1065106, 1521580, 2130212, 2662765, 5325530, 10651060]

    print(a)
    print(b)
    print(c)
    print(d)
