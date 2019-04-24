# mount_device.py
#WER - Added Provision to add an ASCOM mount or Default simulator and added some additional position properties and as well
#      some interlocks between Parked, Unparked and Tracking.
#      Architecturally in terms of the code I am choosing to assume we connect to an ASCOM simulator or to a real mount,
#      and to quickly copy the ascom object properties to first-level object arrtibutes.

#Even as I work, it is obvious logging is coming soon to an applicati0n near us!
#variable rates are not handled by PWI4 so not dealt with properly here.


import json, time
import win32com.client
#from devices import ptr_math_helpers as pmh
from math import cos, radians

class Mount():

    def __init__(self, driver=None):
        self.device_name = 'mnt1'
        self.driver = driver        
        if driver is not None:
            try:
                self.amnt = win32com.client.Dispatch(self.driver)
                self.arot = win32com.client.Dispatch('ASCOM.PWI3.Rotator')
                self.afoc = win32com.client.Dispatch('ASCOM.PWI3.Focuser')
                print(f'Connected to driver:  {self.driver}.')
                self.tracking_ra_rate = 0    #PWI4 does not support rates yet.
                self.tracking_dec_rate = 0
            except:
                self.amnt = win32com.client.Dispatch('ASCOM.Simulator.Telescope')
                print(f'NB NB NB:  Connected to driver: ASCOM.Simulator.Telescope')
                self.tracking_ra_rate = 0    #NB NB NB THis needs fixing
                self.tracking_dec_rate = 0
        self.on_init_connected = self.amnt.Connected = True  #NB NB NB Do we want to do something else if connect fails?
        self.arot_connected = self.arot.Connected = True 
        self.afoc.connected = self.afoc.Connected = True 
        self.driver_version = self.amnt.DriverVersion
        self.interface_version = self.amnt.InterfaceVersion
        #I think these "local" instance variables are not needed and apt to end up stale. Better  use self.amnt....
        #I wonder if better called a_mnt for 'ASCOM mount'?
        self.inst = 'inst_0'
        self.rdsys= 'J.Now'  #This is difficult to deal with, do we transform back to requested Equinox for Ra, Dec...?
        self.is_parked = self.amnt.AtPark
        self.is_tracking = self.amnt.Tracking       
            
    def set_tracking_rates(self, ra_rate_value, dec_rate_value):
        self.tracking_ra_rate = ra_rate_value
        self.tracking_dec_rate = dec_rate_value
        print(f'Tracking rates set to ra: {self.tracking_ra_rate}, dec: {self.tracking_dec_rate}. \n')

    def do_track(self, do_tracking_boolean=True):
        self.amnt.Tracking = do_tracking_boolean
        print(f'Tracking status: {self.amnt.Tracking}')
        
    def allstop(self):
        self.amnt.Tracking  = False
        self.amnt.AbortSlew()
        self.amnt.Tracking  = False
        print(f"Slew Stopped. Tracking off.")

    def park(self):
        if self.amnt.CanPark:
            self.amnt.Park()
        if self.amnt.CanSetTracking:
            self.amnt.Tracking= False
        self.amnt.Tracking  = False
        print('Telescope is parked, and not tracking.')

    def unpark(self):
        if self.amnt.CanPark:
            self.amnt.Unpark()
        if self.amnt.CanSetTracking:
            self.amnt.Tracking= False
        self.amnt.Tracking  = False   #Only turn tracking on after a slew.
        print('Telescope is un-parked, and not tracking.')
    
    def slew_to_eq(self, ra, dec, rdsys):
        #equ = 'J.2000.0, J.2000, B1950, J.now    etc.
        print('mount rdsys:  ', rdsys)
        self.rdsys = rdsys
        if self.amnt.CanSlewAsync:
            self.amnt.SlewToCoordinatesAsync(ra, dec)
        elif self.amnt.CanSlew:
            self.amnt.SlewToCoordinates(ra, dec)
        else:
            print(f'Slewing to ra: {ra}, dec: {dec} failed!')                       
            
        print(f'Slewing to ra: {ra}, dec: {dec}.')

    def slew_to_azalt(self, az, alt):
        self.sys= 'topo'
        if self.amnt.CanSlewAltAzAsync:
            self.amnt.SlewToAltAzAsync(az, alt)
        elif self.amnt.CanSlewAltAz:
            self.amnt.SlewToAltAz(az, alt)
        else:
            print(f'Slewing to az: {az}, alt: {alt} failed!')

        print(f'Slewing to az: {az}, alt: {alt}.')
    

        
    def print_mount_status(self):
        alt = self.amnt.Altitude
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
        ra\t\t\t{self.amnt.RightAscension}
        dec\t\t\t{self.amnt.Declination}
        sid\t\t\t{self.amnt.SiderealTime}
        rdsys\t\t\t{self.rdsys}
        az\t\t\t{self.amnt.Azimuth}
        alt\t\t\t{alt}
        zen\t\t\t{zen}
        air\t\t\t{airmass}
        inst\t\t\t{self.inst}
        rot\t\t\t{self.arot.Rotation}
        focus\t\t\t{self.afoc.Position}
        is_parked\t\t{self.amnt.AtPark}
        is_tracking\t\t{self.amnt.Tracking}
        is_slewing\t\t{self.amnt.Slewing}
        tracking_ra_rate\t{self.tracking_ra_rate}
        tracking_dec_rate\t{self.tracking_dec_rate}
        --------------------------------
        """
        print(status)

    def get_mount_status(self):
        alt = self.amnt.Altitude
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
            f'{self.device_name}_ra': str(self.amnt.RightAscension),
            f'{self.device_name}_dec': str(self.amnt.Declination),
            f'{self.device_name}_sid': str(self.amnt.SiderealTime),
            f'{self.device_name}_rdsys': str(self.rdsys),
            f'{self.device_name}_az': str(self.amnt.Azimuth),
            f'{self.device_name}_alt': str(alt),
            f'{self.device_name}_zen': str(zen),
            f'{self.device_name}_air': str(airmass),
            f'{self.device_name}_inst': str(self.inst),
            f'{self.device_name}_rot': str(self.arot.Position),
            f'{self.device_name}_rot_moving': str(self.arot.IsMoving),
            f'{self.device_name}_focus': str(self.afoc.Position),
            f'{self.device_name}_foctemp': str(self.afoc.Temperature),
            f'{self.device_name}_foc_moving': str(self.afoc.IsMoving),
            f'{self.device_name}_is_parked': (self.amnt.AtPark),
            f'{self.device_name}_is_tracking': str(self.amnt.Tracking),
            f'{self.device_name}_is_slewing': str(self.amnt.Slewing),
            f'{self.device_name}_tracking_ra_rate': str(self.tracking_ra_rate),
            f'{self.device_name}_tracking_dec_rate': str(self.tracking_dec_rate),
            #f'{self.device_name}_timestamp': str(int(time.time()))
        }
        return json.dumps(status)


if __name__=="__main__":
    m = Mount(driver='ASCOM.PWI4.Telescope')
    print(m.get_mount_status())
    m.print_mount_status()