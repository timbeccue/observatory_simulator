# camera_device.py
import json, time, boto3, os
from shutil import copyfile
import win32com.client

class Maxim:

    bucketname = 'pythonbits'

    def __init__(self, driver = None):
        self.maxim_name = 'mdl1'
        self.driver = driver        
        if self.driver is not None:
            try:
                self.amdl = win32com.client.Dispatch(self.driver)
                print(f'Installing driver:   {self.driver}.')
                if not self.amdl.LinkEnabled:
                    print('Enabling link in 2 seconds.')
                    time.sleep(2)
                    self.amdl.LinkEnabled = True
                    time.sleep(0.5)
                print('Link is:  ', self.amdl.LinkEnabled )
                self.amdl.TemperatureSetpoint= -20.0
                self.amdl.CoolerOn = True
            except:
                #self.amdl = win32com.client.Dispatch('ASCOM.Simulator.Camera')
                print('Trying to insall camera simulator, something failed.')

        self.binX = 1
        self.binY = 1
        self.last_exposure_time = 0
        self.last_image_name = 'empty'
        self.images = []

        self.image_number = 0

    def start_exposure(self, site, duration):
        print(f"started {duration} second exposure.")
        self.last_exposure_time = duration
        self.last_image_name = f'{int(time.time())}_{site}_testimage_{duration}s_no{self.image_number}.jpg'
        print(f"image file: {self.last_image_name}")
        self.images.append(self.last_image_name)
        #self.save_image(self.last_image_name)
        self.image_number += 1
        return self.last_image_name

    def save_image(self, image_name):
        cwd = os.path.dirname(__file__)
        source_file = os.path.join(cwd, 'data/base.jpg')
        create_file = os.path.join(cwd, 'data/'+image_name)
        copyfile(source_file, create_file)


    def get_maxim_status(self):
        status = {
            f'{self.maxim_name}_binX': str(self.binX),
            f'{self.maxim_name}_binY': str(self.binY),
            f'{self.maxim_name}_last_exposure_time': str(self.last_exposure_time),
            f'{self.maxim_name}_last_image_name': self.last_image_name,
        }
        return json.dumps(status)
    
class Helper:

    bucketname = 'pythonbits'

    def __init__(self, driver = None):
        self.helper_name = 'madlh1'
        self.driver = driver        
        if self.driver is not None:
            try:
                self.amxh = win32com.client.Dispatch(self.driver)
                print(f'Installing driver:   {self.driver}.')
                self.amxh.TelescopeConnected = True
                self.amxh.FocuserConnected = True
                #Maxim does not support explicit Rotator connection.
            except:
                self.amxh = win32com.client.Dispatch('ASCOM.Simulator.Camera')
        #THis needs filling out.l

    def get_helper_status(self):
        status = {
            f'{self.helper_name}_helper status found here': str(self.helper_name)    
        }
        return json.dumps(status)

class Camera:

    bucketname = 'pythonbits'

    def __init__(self):
        self.camera_name = 'cam1'
        print(f'Installing driver:   {self.camera_name}.')
        self.binX = 1
        self.binY = 1
        self.last_exposure_time = 0
        self.last_image_name = 'empty'
        self.images = []

        self.image_number = 0

    def start_exposure(self, site, duration):
        print(f"started {duration} second exposure.")
        self.last_exposure_time = duration
        self.last_image_name = f'{int(time.time())}_{site}_testimage_{duration}s_no{self.image_number}.jpg'
        print(f"image file: {self.last_image_name}")
        self.images.append(self.last_image_name)
        #self.save_image(self.last_image_name)
        self.image_number += 1
        return self.last_image_name

    def save_image(self, image_name):
        cwd = os.path.dirname(__file__)
        source_file = os.path.join(cwd, 'data/base.jpg')
        create_file = os.path.join(cwd, 'data/'+image_name)
        copyfile(source_file, create_file)


    def get_camera_status(self):
        status = {
            f'{self.camera_name}_binX': str(self.binX),
            f'{self.camera_name}_binY': str(self.binY),
            f'{self.camera_name}_last_exposure_time': str(self.last_exposure_time),
            f'{self.camera_name}_last_image_name': self.last_image_name,
        }
        return json.dumps(status)


if __name__=="__main__":
    c = Maxim(driver='Maxim.CCDCamera')
    ch = Helper(driver='Maxim.Application')
    #cc = Camera()
    print(c.get_maxim_status(), ch.get_helper_status())#, cc.get_camera_status())

