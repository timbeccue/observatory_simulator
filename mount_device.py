# mount_device.py
import json, time

class Mount():

    def __init__(self):
        self.ra = 0
        self.dec = 0
        self.is_parked = True
        self.is_tracking = False
        self.tracking_ra_rate = 0
        self.tracking_dec_rate = 0

    def set_tracking_rates(self, ra_rate_value, dec_rate_value):
        self.tracking_ra_rate = ra_rate_value
        self.tracking_dec_rate = dec_rate_value
        print(f'Tracking rates set to ra: {self.tracking_ra_rate}, dec: {self.tracking_dec_rate}. \n')

    def do_track(self, do_tracking_boolean=True):
        self.is_tracking = do_tracking_boolean
        print(f'Tracking status: {self.is_tracking}')

    def all_stop(self):
        self.is_tracking = False
        print(f"Slew aborted. Tracking off.")

    def park(self):
        self.is_parked = True
        print('Telescope is parked.')

    def slew_to_eq(self, ra, dec):
        self.is_parked = False
        self.ra = ra
        self.dec = dec
        print(f'Slewing to ra: {self.ra}, dec: {self.dec}.')

    def print_mount_status(self):
        status = f"""
        --------------------------------
        Mount Status:
        ra\t\t\t{self.ra}
        dec\t\t\t{self.dec}
        is_parked\t\t{self.is_parked}
        is_tracking\t\t{self.is_tracking}
        tracking_ra_rate\t{self.tracking_ra_rate}
        tracking_dec_rate\t{self.tracking_dec_rate}
        --------------------------------
        """
        print(status)
    
    def get_mount_status(self):
        status = {
            'ra': str(self.ra),
            'dec': str(self.dec),
            'is_parked': str(self.is_parked),
            'is_tracking': str(self.is_tracking),
            'tracking_ra_rate': str(self.tracking_ra_rate),
            'tracking_dec_rate': str(self.tracking_dec_rate),
            'timestamp': str(int(time.time()))
        }
        return json.dumps(status)


if __name__=="__main__":
    m = Mount()
    m.get_mount_status()