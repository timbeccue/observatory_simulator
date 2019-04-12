import threading
import time
import sys

store = []

def gen(i=0):
    while True:
        yield i
        i += 1 

g = gen()

def take(): 
    while True:
        store.pop(0)
        print(store)
        time.sleep(2)

def add():
    while True:
        store.append(next(g))
        print(store)
        time.sleep(1)


take_thread = threading.Thread(target=take)
add_thread = threading.Thread(target=add)

add_thread.start()
time.sleep(2)
take_thread.start()