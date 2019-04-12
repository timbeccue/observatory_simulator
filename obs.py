
# obs.py

import sqs, mount_device 
import time, json
from random import randint
from tqdm import tqdm


class Observatory:

    def __init__(self): 
        self.q = sqs.Queuer() 
        self.m = mount_device.Mount()
        self.run()

    def run(self):
        while True:
            # Scan for a new task
            new_message = self.q.read_queue_item()
            # If there's new work, do it.
            if new_message is not False:
                self._do_request(json.loads(new_message))
            time.sleep(1)


    def _do_request(self, r):
        command = r['command']
        if command == 'goto':
            self.m.slew_to_eq(r['ra'], r['dec'])
            self._progress()
        if command == 'park':
            self.m.park()
            self._progress()


    def _progress(self):
        """ 
        Show dummy progress bar to simulate activity.
        """
        for k in tqdm(range(100000 * randint(1,20)**2), ncols=70):
            pass


if __name__=="__main__":
    wmd = Observatory()
