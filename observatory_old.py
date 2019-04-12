# observatory.py

import sqs, mount_device 
import time, json, threading
from random import randint
from pynput import keyboard
from tqdm import tqdm

lock = threading.Lock()

class Observatory():

    def __init__(self): 
        self.q = sqs.Queuer() 
        self.m = mount_device.Mount()
        self.messages = []

        self.run()

    def run(self):

        read_thread = threading.Thread(target=self.read_q, name='reading_thread')
        parse_thread = threading.Thread(target=self.parse_q, name='parsing_thread')

        read_thread.start()            
        parse_thread.start()

    def read_q(self):
        while True:
            new_messages = self.q.read_queue()
            for m in new_messages:
                self.messages.append(m)
                print(f"Pending messages: {len(self.messages)}")
            #time.sleep(0.5)
        #for request in messages:
        #    request = json.loads(request)
        #    print(json.dumps(request, indent=2))
        #    self.do_request(request)

    def parse_q(self):
        while True:
            pending = len(self.messages)
            if pending > 0:
                for _ in range(pending):
                    #print(f"type is {type(self.messages.pop(0))}")
                    request = json.loads(self.messages.pop(0))
                    #lock.acquire()
                    #print('lock acquired')
                    self.do_request(request)
                    #lock.release()
                    #print('lock released')
                    print(f"Pending messages: {len(self.messages)}")
            #time.sleep(0.5)
        

           

    def do_request(self, r):

        command = r['command']

        if command == 'goto':
            self.m.slew_to_eq(r['ra'], r['dec'])
            self.progress()

        if command == 'park':
            self.m.park()
            self.progress()


    def progress(self):
        """ 
        Show dummy progress bar to simulate activity.
        """
        lock.acquire()
        print('lock acquired')
        for k in tqdm(range(100000 * randint(1,20)**2), ncols=70):
            pass
        lock.release()
        print('lock released')



if __name__=="__main__":
    wmd = Observatory()
