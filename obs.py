
# obs.py

from devices import mount_device, camera_devices, pwi_devices
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
        #The line below is a specific instance of a configuratin which needs to be owner specified.
        self.m = mount_device.Mount(driver='ASCOM.PWI4.Telescope')
        self.r = pwi_devices.Rotator(driver='ASCOM.PWI3.Rotator')
        self.fc = pwi_devices.Focuser(driver='ASCOM.PWI3.Focuser')
        #self.cc = camera_devices.Camera()
        self.c = camera_devices.Camera(driver='ASCOM.Simulator.Camera')
        #self.ch = camera_devices.Helper(driver='Maxim.Application')
        print('camera object at:  ', self.c, self.c.acam)
        #print(self.c.amdl.Filter)

        self.d = r.make_dynamodb(self.name)
        self.q = r.make_sqs(self.name)
        self.s = r.make_s3(self.name)

        self.run()
        
        #                camera_1_app = win32com.client.Dispatch("Maxim.Application")
#                camera_1= win32com.client.Dispatch("Maxim.CCDCamera")
#                #doc = win32com.client.Dispatch("Maxim.Document")   #Envoking this creates an empty image.
#                camera_1.LinkEnabled = True
#                camera_1_app.TelescopeConnected = True
#                camera_1_app.FocuserConnected = True
#                camera_1.CoolerOn = True
#                if camera_1.LinkEnabled and camera_1_app.TelescopeConnected and camera_1_app.FocuserConnected \
#                   and camera_1.CoolerOn:
#                    print("Maxim appears connected.")

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
            self.m.slew_to_eq(float(r['ra']), float(r['dec']), r['rdsys'])
            self._progress()
        if command == 'goto_azalt':
            self.m.slew_to_azalt(float(r['az']), float(r['alt']))
            print(self.name)
            self._progress()
        if command == 'allstop':
            self.m.allstop()
            self._progress()
        if command == 'park':
            print('park:  ', self, self.m)
            self.m.park()
            self._progress()
        if command == 'unpark':
            self.m.unpark()
            self._progress()
        if command == 'expose':
            print('Trying:  ', self, self.name, self.c)
            print("deeper;  ", self.c.acam)
            print("deepest;  ", self.c.acam.NumX)
            self.c.start_exposure(self.name, r['duration'], r['filter'], r['repeat'])
            filename = 'dummy.jpeg'  #self.c.start_exposure(self.name, r['duration'], r['filter'], r['repeat'])
            self._progress(r['duration'])
            self.s.upload_file(filename)   #SEnd to S3

            

    def update_status(self):
        while True:
            m_status = json.loads(self.m.get_mount_status())
            c_status = json.loads(self.c.get_camera_status())
            #ch_status = json.loads(self.ch.get_helper_status())
            r_status = json.loads(self.r.get_rotator_status())
            fc_status = json.loads(self.fc.get_focuser_status())

            status ={**m_status, **c_status, **r_status, **fc_status}#, **ch_status}

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
    print('sites:  ', sites)
    for site in sites:
        observatories[site] = Observatory(site)

