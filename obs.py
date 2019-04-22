
# obs.py

from devices import mount_device, camera_device 
import time, json
from random import randint
from tqdm import tqdm 
import threading
from aws.init_resources import Resources as r


class Observatory:

    update_status_period = 5 #seconds
    scan_for_tasks_period = 2

    def __init__(self, name): 
        self.name = name
        self.m = mount_device.Mount()
        self.c = camera_device.Camera()

        self.d = r.make_dynamodb(self.name)
        self.q = r.make_sqs(self.name)
        self.s = r.make_s3(self.name)

        self.run()

    def run(self):
        """
        Run two loops in separate threads:
        - Update status regularly to dynamodb.
        - Get commands from sqs and execute them.
        """
        threading.Thread(target=self.update_status).start()
        threading.Thread(target=self.scan_requests).start()


    def scan_requests(self):
        while True:
            # Scan for a new task
            new_message = self.q.read_queue_item()
            # If there's new work, do it.
            if new_message is not False:
                self._do_request(json.loads(new_message))
            #self.update_status()
            time.sleep(self.scan_for_tasks_period)

    def _do_request(self, r):
        command = r['command']
        if command == 'goto':
            self.m.slew_to_eq(r['ra'], r['dec'])
            print(self.name)
            self._progress()
        if command == 'park':
            self.m.park()
            self._progress()
        if command == 'expose':
            filename = self.c.start_exposure(self.name, r['duration'])
            self._progress(r['duration'])
            self.s.upload_file(filename)

            

    def update_status(self):
        while True:
            m_status = json.loads(self.m.get_mount_status())
            c_status = json.loads(self.c.get_camera_status())

            status ={**m_status, **c_status}

            # Include index key/val: key 'State' with value 'State'.
            status['State'] = 'State'
            status['site'] = self.name
            status['timestamp'] = str(int(time.time()))
            try:
                self.d.insert_item(status)
            except:
                print("Error sending to dynamodb.")
                print("If this is a new site, dynamodb might still be initializing.") 
                print("Please wait a minute and try again.")

            time.sleep(self.update_status_period)

    def _progress(self, duration=None):
        """ 
        Show dummy progress bar to simulate activity.
        Optional time param specifies approx duration.
        """
        if duration is None:
            for _ in tqdm(range(100000 * randint(1,20)**2), ncols=70, bar_format='{desc}: {percentage:3.0f}%|{bar}| simulating activity '):
                pass
        else:
            #for k in tqdm(range(int(float(duration)*1000)), ncols=70):
            #    time.sleep(0.001)
            steps = int(100*duration)
            with tqdm(total=steps*10, ncols=70, bar_format='{desc}: {percentage:3.0f}%|{bar}| simulated exposing: {elapsed_s:3.00f} s') as tbar:
                for _ in range(steps):
                    time.sleep(0.01)
                    tbar.update(10)


if __name__=="__main__":
    observatories = {}
    resources = r("sites_config.yml")
    sites = resources.get_all_sites()
    for site in sites:
        observatories[site] = Observatory(site)

