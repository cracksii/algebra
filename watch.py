import time

n = 8
def watch(a, *args):
    def wrapper(*args, **kwargs):
        start = time.time()
        r = a(*args, **kwargs)
        print(f'{a} --- {round(time.time() - start, n)}s')
        return r
    return wrapper
