# camera_device.py
import json, time, boto3, os
from shutil import copyfile
import threading
import win32com.client
from astropy.io import fits
import numpy as np

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
        self.sel_filter = 'unknown'
        self.filters = ['air', 'dif', 'w', 'CR', 'N2', 'u', 'g', 'r', 'i', 'zs', \
                   'PL', 'PR', 'PG', 'PB', 'O3', 'HA', 'S2', 'dif_u', 'dif_g',
                   'dif_r', 'dif_i', 'dif_zs', 'dark']
        self.filter_index = [(0, 0), (4, 0), (2, 0), (1, 0), (3, 0), (0, 5), (0, 6), (0, 7), (0, 8), (5, 0), \
                    (0, 4), (0, 3), (0, 2), (0, 1), (7, 0), (6, 0), (8, 0), (4, 5), (4, 6), \
                    (4, 7), (4, 8), (9, 0), (10, 9), (-1,-1),  (-1,-1), (-1,-1), (-1,-1),  \
                    (-1,-1),  (-1,-1)]
        self.last_exposure_time = 0
        self.last_image_name = 'empty'
        self.images = []

        self.image_number = 0

    def start_exposure(self, site, duration, sel_filter, repeat):
        print(f"started {duration} second exposure.")
        self.last_exposure_time = duration
        self.repeat = int(repeat)
        if 0 <= int(sel_filter) < len(self.filters):
            self.sel_filter = self.filters[int(sel_filter)]
        #Real work starts here
        print('pre-testing actualexosure:  ', self, self.amdl)
        #self.amdl.Filter = self.sel_filter   #This may take time to run.
        self.amdl.expose(self.last_exposure_time, 1, 3)   #1 is for light frame.Will take time to run.
        #Maxim will autsave for now into Q:\\archive\\eao3
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
            f'{self.maxim_name}_filters': str(self.filters),
            f'{self.maxim_name}_sel_filter': str(self.sel_filter),
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

    def __init__(self, driver=None):
        self.camera_name = 'cam1'
        print(f'Installing driver:   {self.camera_name}.')
        self.driver = driver        
        if self.driver is not None:
            try:
                self.acam = win32com.client.Dispatch(self.driver)
                print(f'Installing driver:   {self.driver}.')
                if not self.acam.Connected:
                    print('Enabling link in 2 seconds.')
                    time.sleep(2)
                    self.acam.Connected = True
                    time.sleep(0.5)
                print('Link is:  ', self.acam.Connected)
                #self.acam.SetCCDTemperature = -20.0
                #self.acam.CoolerOn = True
            except:
                #self.amdl = win32com.client.Dispatch('ASCOM.Simulator.Camera')
                print('Trying to install camera simulator, something failed.')
        self.binX = 1
        self.binY = 1
        self.last_exposure_time = 0
        self.last_image_name = 'empty'
        self.images = []
        self.exposing = False
        self.img_available = False
        self.image_number = 0
        self.run()
        
    def run(self):
        """
        Run two loops in separate threads:
        - Update status regularly to dynamodb.
        - Get commands from sqs and execute them.
        """
        threading.Thread(target=self.finish_exposure).start()

    def start_exposure(self, site, duration, filter, repeat):
        print(f"started {duration} second exposure.")
        self.last_exposure_time = duration
        self.acam.StartExposure(duration, True)
        self.img_available = False
        self.exposing = True
        self.last_image_name = f'{int(time.time())}_{site}_testimage_{duration}s_no{self.image_number}.jpg'
        print(f"image file: {self.last_image_name}")
        self.images.append(self.last_image_name)
        #self.save_image(self.last_image_name)
        self.image_number += 1
        return self.last_image_name
    
    def finish_exposure(self):
        while True:
            try:
                if self.img_available:
                    print(self.img[0][:5])
                    print("Big 20 second delay here")
                    try:
                        hdu = fits.PrimaryHDU(self.img)
                        hdu.header['OBSERVER'] = ("WER", 'unit = Person')
                        hdu.writeto('Q:\\archive\\ea03\\new2.fits', overwrite=True)
                    except:
                        print(f'Fits file write failed.')
                    self.img_available = False
                    self.img = None
                    hdu = None
                    print("End of20 second delay")
            except:
                pass

            time.sleep(.5)

    def save_image(self, image_name):
        cwd = os.path.dirname(__file__)
        source_file = os.path.join(cwd, 'data/base.jpg')
        create_file = os.path.join(cwd, 'data/'+image_name)
        copyfile(source_file, create_file)


    def get_camera_status(self):
        try:
            state = self.acam.CameraState
            ready = self.acam.ImageReady
            if state == 0:
                status = {f'{self.camera_name}_state': 'Camera Idle'}
            elif state == 1:
                status = {f'{self.camera_name}_state': 'Camera Waiting'}
            elif state == 2:
                status = {f'{self.camera_name}_state': 'Camera Exposing'}
            elif state == 3:
                status = {f'{self.camera_name}_state': 'Camera Reading'}
            elif state == 4:
                status = {f'{self.camera_name}_state': 'Camera Downloding'}
            elif state == 5:
                status = {f'{self.camera_name}_state': 'Camera Error'}
            else:
                status = {f'{self.camera_name}_state': 'No Status Available'}
            if self.exposing:
                status[f'{self.camera_name}_exposing'] = 'Cam Exposing'
            else:
                status[f'{self.camera_name}_exposing'] = 'Cam Idle'
                
            if ready and self.exposing:
                status[f'{self.camera_name}_imgavail'] = 'Image Ready'
            else:
                status[f'{self.camera_name}_imgavail'] = 'Image Not Ready'
            if ready and self.exposing:
                print('reading Array')
                self.img = self.acam.ImageArray
                self.img_available = True
                self.exposing = False
    
        except:
            status = {f'{self.camera_name}_status': "None Available"}
        return json.dumps(status)


if __name__=="__main__":
    #c = Maxim(driver='Maxim.CCDCamera')
    #ch = Helper(driver='Maxim.Application')
    #cc = Camera()
    c = Camera('ASCOM.Simulator.Camera')
    #print(c.get_camera_status())#, ch.get_helper_status())#, cc.get_camera_status())

