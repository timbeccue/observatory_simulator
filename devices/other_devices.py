# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 13:43:01 2019

@author: obs
"""



import json, time
import win32com.client
#from devices import ptr_math_helpers as pmh


class Rotator():

    def __init__(self, driver=None):
        self.device_name = 'mnt1'
        self.driver = driver        
        if driver is not None:
            try:
                self.arot= win32com.client.Dispatch(self.driver)
                print(f'Connected to driver:  {self.driver}.')
            except:
                self.arot= win32com.client.Dispatch('ASCOM.Simulator.ROTATOR')
                print(f'NB NB NB:  Connected to driver: ASCOM.Simulator.Rotator')
        self.on_init_connected = self.arot.Connected = True  #NB NB NB Do we want to do something else if connect fails?
        
    def print_rot_status(self):

        status = f"""
        --------------------------------
        Rotator Status:
        rotation\t\t\t{self.arot.Position}
        rot_moving\t\t\t{self.arot.IsMoving}
        --------------------------------
        """
        print(status)

    def get_rot_status(self):

        status = {
            f'{self.device_name}_rotation': str(self.arot.Position),
            f'{self.device_name}_rot_moving': str(self.arot.IsMoving),
        }
        return json.dumps(status)
        
class Focuser():

    def __init__(self, driver=None):
        self.device_name = 'mnt1'
        self.driver = driver        
        if driver is not None:
            try:
                self.afoc = win32com.client.Dispatch(self.driver)
                print(f'Connected to driver:  {self.driver}.')
            except:
                self.afoc = win32com.client.Dispatch('ASCOM.Simulator.Focuser')
                print(f'NB NB NB:  Connected to driver: ASCOM.Simulator.Focuser')
        self.on_init_connected = self.afoc.Connected = True  #NB NB NB Do we want to do something else if connect fails?
        
    def print_foc_status(self):

        status = f"""
        --------------------------------
        Focus Status:
        focus\t\t\t{self.afoc.Position}
        foctemp\t\t\t{self.afoc.Temperature}
        foc_moving\t\t\t{self.afoc.IsMoving}
        --------------------------------
        """
        print(status)

    def get_foc_status(self):

        status = {
            f'{self.device_name}_focus': str(self.afoc.Position),
            f'{self.device_name}_foctemp': str(self.afoc.Temperature),
            f'{self.device_name}_foc_moving': str(self.afoc.IsMoving),
        }
        return json.dumps(status)


if __name__=="__main__":
    r = Rotator(driver='ASCOM.PWI3.Rotator')
    fc = Focuser(driver='ASCOM.PWI3.Focuser')
    print(r.get_rot_status())
    r.print_rot_status()
    print(fc.get_foc_status())
    fc.print_foc_status()