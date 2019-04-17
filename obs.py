
# obs.py

import sqs, dynamodb, s3, mount_device, camera_device 
import time, json, yaml
from random import randint
from tqdm import tqdm
import threading

def init_resources(configfile):

    all_queues = {} 
    all_dynamodb = {} 

    with open(configfile, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            sites = config['Sites'].keys() 
            return list(sites)

        except yaml.YAMLError as exc:
            print(exc)

def make_queues(sitename):
    fromAWS = sitename + '_from_aws_pythonbits.fifo'
    toAWS = sitename + '_to_aws_pythonbits.fifo'
    return sqs.Queuer(fromAWS, toAWS)

def make_dynamodb(sitename):
    tablename = sitename + "_state_pythonbits"
    return dynamodb.DynamoDB(tablename) 

class Observatory:

    update_status_period = 5 #seconds
    scan_for_tasks_period = 2

    def __init__(self, name): 
        self.name = name
        self.m = mount_device.Mount()
        self.c = camera_device.Camera()

        self.d = make_dynamodb(self.name)
        self.q = make_queues(self.name)
        self.s = s3.S3(self.name)

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
            self.d.insert_item(status)

            time.sleep(self.update_status_period)

    def _progress(self, duration=None):
        """ 
        Show dummy progress bar to simulate activity.
        Optional time param specifies approx duration.
        """
        if duration is None:
            for k in tqdm(range(100000 * randint(1,20)**2), ncols=70):
                pass
        else:
            for k in tqdm(range(int(float(duration)*1000)), ncols=70):
                time.sleep(0.001)


if __name__=="__main__":
    observatories = {}
    sites = init_resources("sites_config.yml")
    for site in sites:
        observatories[site] = Observatory(site)

