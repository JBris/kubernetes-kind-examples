#!/user/bin/env python

import ray

@ray.remote
def square(x):
    return x*x

def main():
    futures = [
        square.remote(i) for i in range(5)
    ]

    print(ray.get(futures))

if __name__ == "__main__":
    main()