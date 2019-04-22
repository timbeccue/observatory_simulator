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

        # Filename for the image. The upload_file method in s3 saves the image with this name. 
        # The filename does not include the directory structure where it will live in s3.
        self.last_image_name = f'{int(time.time())}_{site}_testimage_{duration}s_no{self.image_number}.jpg'
        print(f"image file: {self.last_image_name}")

        # Add to list of all images taken with this camera
        self.images.append(self.last_image_name)
        #self.save_image(self.last_image_name)
        self.image_number += 1
        return self.last_image_name

    def save_image(self, image_name):
        """
        Simulate saving an image by duplicating our hardcoded test image.
        Currently not used, but I'm keeping it here for reference.
        """
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

