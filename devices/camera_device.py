# camera_device.py
import json, time, boto3, os
from shutil import copyfile
import win32com.client

class MaximCamera():

    bucketname = 'pythonbits'

    def __init__(self, driver= None):
        self.camera_name = 'max1'
        self.driver = driver        
        if self.driver is not None:
            try:
                self.amdl = win32com.client.Dispatch(self.driver)
                print(f'Installing driver:  {self.driver}.')
                self.amdl.LinkEnabled = True
                self.amdl.TemperatureSetpoint= -20.0
                self.amdl.CoolerOn = True
            except:
                #self.amdl = win32com.client.Dispatch('ASCOM.Simulator.Camera')
                print('Trying to insall camera simulator, somethig failed.')

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
    
    #                camera_1.LinkEnabled = True
#                camera_1_app.TelescopeConnected = True
#                camera_1_app.FocuserConnected = True
#                camera_1.CoolerOn = True
#                if camera_1.LinkEnabled and camera_1_app.TelescopeConnected and camera_1_app.FocuserConnected \
#                   and camera_1.CoolerOn:
#                    print("Maxim appears co

class MaximHelper():

    bucketname = 'pythonbits'

    def __init__(self, driver = None):
        self.camera_name = 'maxh1'
        self.driver = driver        
        if self.driver is not None:
            try:
                self.amxh = win32com.client.Dispatch(self.driver)
                print(f'Installing driver:  {self.driver}.')
                self.amxh.TelescopeConnected = True
                self.amxh.FocuserConnected = True
                #Maxim does not support explicit Rotator connection.
            except:
                self.amxh = win32com.client.Dispatch('ASCOM.Simulator.Camera')
        #THis needs filling out.l




    def get_camera_status(self):
        status = {
            f'{self.camera_name}_binX': str(self.binX),
            f'{self.camera_name}_binY': str(self.binY),
            f'{self.camera_name}_last_exposure_time': str(self.last_exposure_time),
            f'{self.camera_name}_last_image_name': self.last_image_name,
        }
        return json.dumps(status)

class Camera:

    bucketname = 'pythonbits'

    def __init__(self):
        self.camera_name = 'cam1'
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
    c = MaximCamera(driver='Maxim.CCDCamera')
    ch = MaximHelper(driver='Maxim.Application')
    print(c.get_camera_status())

