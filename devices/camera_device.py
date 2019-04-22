# camera_device.py
import json, time, boto3, os
from shutil import copyfile

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
    m = Camera()
    print(m.get_camera_status())

