# observatory.py

import sqs, mount_device 
import time, json
from random import randint
from pynput import keyboard
from tqdm import tqdm


class Observatory():

    def __init__(self): 
        self.q = sqs.Queuer() 
        self.m = mount_device.Mount()
        self.keyBuffer = []

        self.run()

    def run(self):

        # Listen for keypresses. 'Space, backspace, space, backspace' will prompt another queue read.
        #listener = keyboard.Listener( on_press=self.read_q ) 
        #listener.start()

        # Infinite loop keeps program running until manual termination.
        while True:
            time.sleep(1)
            self.read_q()

    def read_q(self):

        #self.keyBuffer.append(str(key).strip("'"))        
        #self.keyBuffer = self.keyBuffer[-4:] # store last 4 inputs in a buffer

        # Typing 'space, backspace, space, backspace' anywhere will initiate another read of the queue.
        #if self.keyBuffer == ['Key.space','Key.backspace','Key.space','Key.backspace']:
        messages = self.q.read_queue()
        for request in messages:
            #self.do_request(request)
            request = json.loads(request)
            print(json.dumps(request, indent=2))
            if request['command'] == 'goto': 
                self.m.slew_to_eq(request['ra'],request['dec'])
                for k in tqdm(range(10000 * randint(1,20)**2), ncols=100):
                    pass
                print()
            

    def do_request(self, request):

        body = json.loads(request)
        #print(f"request: {request}, {type(request)}")

        print()
        device = body['device']
        print(f"Device: {device}")

        command = body['command']
        print(f"Command: {command}")

        params = {key:body[key] for key in body if key not in ['device', 'command']}
        print(params)

        print(f"Executing requested action")
        for k in tqdm(range(10000 * randint(1,20)**2), ncols=100):
            pass



if __name__=="__main__":
    wmd = Observatory()
