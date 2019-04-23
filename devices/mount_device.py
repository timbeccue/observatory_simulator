# mount_device.py
#WER - Added Provision to add an ASCOM mount or Default simulator and added some additional position properties and as well
#      some interlocks between Parked, Unparked and Tracking.
#      Architecturally in terms of the code I am choosing to assume we connect to an ASCOM simulator or to a real mount,
#      and to quickly copy the ascom object properties to first-level object arrtibutes.

#Even as I work, it is obvious logging is coming soon to an applicati0n near us!
#variable rates are not handled by PWI4 so not dealt with properly here.


import json, time
import win32com.client
from devices import ptr_math_helpers as pmh
from math import cos, radians

class Mount():

    def __init__(self, driver=None):
        self.device_name = 'mnt1'
        self.driver = driver        
        if driver is not None:
            try:
                self.mount = win32com.client.Dispatch(self.driver)
                print(f'Connected to driver:  {self.driver}.')
                self.tracking_ra_rate = 0    #PWI4 does not support rates yet.
                self.tracking_dec_rate = 0
            except:
                self.mount = win32com.client.Dispatch('ASCOM.Simulator.Telescope')
                print(f'NB NB NB:  Connected to driver: ASCOM.Simulator.Telescope')
                self.tracking_ra_rate = 0    #NB NB NB THis needs fixing
                self.tracking_dec_rate = 0
        self.on_init_connected = self.mount.Connected = True  #NB NB NB Do we want to do something else if connect fails?
        self.driver_version = self.mount.DriverVersion
        self.interface_version = self.mount.InterfaceVersion
        #I think these "local" instance variables are not needed and apt to end up stale. Better  use self.mount....
        #I wonder if better called a_mnt for 'ASCOM mount'?
        self.inst = 'inst_0'
        self.sys= 'J.Now'  #This is difficult to deal with, do we transform back to requested Equinox for Ra, Dec...?
        self.is_parked = self.mount.AtPark
        self.is_tracking = self.mount.Tracking       
            
    def set_tracking_rates(self, ra_rate_value, dec_rate_value):
        self.tracking_ra_rate = ra_rate_value
        self.tracking_dec_rate = dec_rate_value
        print(f'Tracking rates set to ra: {self.tracking_ra_rate}, dec: {self.tracking_dec_rate}. \n')

    def do_track(self, do_tracking_boolean=True):
        self.mount.Tracking = do_tracking_boolean
        print(f'Tracking status: {self.mount.Tracking}')
        
    def allstop(self):
        self.mount.Tracking  = False
        self.mount.AbortSlew()
        self.mount.Tracking  = False
        print(f"Slew Stopped. Tracking off.")

    def park(self):
        if self.mount.CanPark:
            self.mount.Park()
        if self.mount.CanSetTracking:
            self.mount.Tracking= False
        self.mount.Tracking  = False
        print('Telescope is parked, and not tracking.')

    def unpark(self):
        if self.mount.CanPark:
            self.mount.Unpark()
        if self.mount.CanSetTracking:
            self.mount.Tracking= False
        self.mount.Tracking  = False   #Only turn tracking on after a slew.
        print('Telescope is un-parked, and not tracking.')
    
    def slew_to_eq(self, ra, dec, sys):
        #equ = 'J.2000.0, J.2000, B1950, J.now    etc.
        self.sys = sys
        if self.mount.CanSlewAsync:
            self.mount.SlewToCoordinatesAsync(ra, dec)
        elif self.mount.CanSlew:
            self.mount.SlewToCoordinates(ra, dec)
        else:
            print(f'Slewing to ra: {ra}, dec: {dec} failed!')                       
            
        print(f'Slewing to ra: {ra}, dec: {dec}.')

    def slew_to_azalt(self, az, alt):
        self.sys= 'topo'
        if self.mount.CanSlewAltAzAsync:
            self.mount.SlewToAltAzAsync(az, alt)
        elif self.mount.CanSlewAltAz:
            self.mount.SlewToAltAz(az, alt)
        else:
            print(f'Slewing to az: {az}, alt: {alt} failed!')

        print(f'Slewing to az: {az}, alt: {alt}.')
    

        
    def print_mount_status(self):
        alt = self.mount.Altitude
        zen = (90 - alt)
        if zen > 90:
            zen = 90.0
        if zen < 0.1:    #This can blow up when zen <=0!
            new_z = 0.01
        else:
            new_z = zen
        sec_z = 1/cos(radians(new_z))
        airmass = round(sec_z - 0.0018167*(sec_z - 1) - 0.002875*((sec_z - 1)**2) - 0.0008083*((sec_z - 1)**3),3)
        status = f"""
        --------------------------------
        Mount Status:
        ra\t\t\t{self.mount.RightAscension}
        dec\t\t\t{self.mount.Declination}
        sid\t\t\t{self.mount.SiderealTime}
        equ\t\t\t{self.sys}
        az\t\t\t{self.mount.Azimuth}
        alt\t\t\t{alt}
        zen\t\t\t{zen}
        air\t\t\t{airmass}
        air\t\t\t{self.inst}
        is_parked\t\t{self.mount.AtPark}
        is_tracking\t\t{self.mount.Tracking}
        is_slewing\t\t{self.mount.Slewing}
        tracking_ra_rate\t{self.tracking_ra_rate}
        tracking_dec_rate\t{self.tracking_dec_rate}
        --------------------------------
        """
        print(status)

    def get_mount_status(self):
        alt = self.mount.Altitude
        zen = (90 - alt)
        if zen > 90:
            zen = 90.0
        if zen < 0.1:    #This can blow up when zen <=0!
            new_z = 0.01
        else:
            new_z = zen
        sec_z = 1/cos(radians(new_z))
        airmass = round(sec_z - 0.0018167*(sec_z - 1) - 0.002875*((sec_z - 1)**2) - 0.0008083*((sec_z - 1)**3),3)
        status = {
            f'{self.device_name}_ra': str(self.mount.RightAscension),
            f'{self.device_name}_dec': str(self.mount.Declination),
            f'{self.device_name}_sid': str(self.mount.SiderealTime),
            f'{self.device_name}_sys': str(self.sys),
            f'{self.device_name}_az': str(self.mount.Azimuth),
            f'{self.device_name}_alt': str(alt),
            f'{self.device_name}_zen': str(zen),
            f'{self.device_name}_air': str(airmass),
            f'{self.device_name}_inst': str(self.inst),
            f'{self.device_name}_is_parked': (self.mount.AtPark),
            f'{self.device_name}_is_tracking': str(self.mount.Tracking),
            f'{self.device_name}_is_slewing': str(self.mount.Slewing),
            f'{self.device_name}_tracking_ra_rate': str(self.tracking_ra_rate),
            f'{self.device_name}_tracking_dec_rate': str(self.tracking_dec_rate),
            #f'{self.device_name}_timestamp': str(int(time.time()))
        }
        return json.dumps(status)


if __name__=="__main__":
    m = Mount(driver='ASCOM.PWI4.Telescope')
    print(m.get_mount_status())
    m.print_mount_status()