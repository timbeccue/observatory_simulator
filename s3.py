import boto3
import os
from botocore.client import Config


class S3:

    # Get the service client with sigv4 configured
    s3_c = boto3.client('s3', 'us-east-1', config=Config(signature_version='s3v4'))

    bucket_name = 'pythonbits'

    def __init__(self, site_name):

        self.bucket = self.s3_c.create_bucket(Bucket=self.bucket_name)
        self.site_name = site_name

    def upload_file(self, to_filename):
        from_file = 'data/base.jpg'
        dirpath = os.path.abspath(os.path.dirname(__file__))
        from_filename = os.path.join(dirpath, from_file)
        try:
            response = self.s3_c.upload_file(
                from_filename, 
                self.bucket_name, 
                to_filename,
                ExtraArgs={
                    'ACL':'public-read',
                    'ContentType': 'image/jpg'
                    }
                )    

            print("file upload success")
        except Exception as e:
            print(f"error uploading to s3: {e}")

    def get_image_url(self, filename):
        params = {
            'Bucket': str(self.bucket_name),
            'Key': str(filename)
        }
        url = self.s3_c.generate_presigned_url(
            ClientMethod='get_object', 
            Params=params,
            ExpiresIn=3600
        )
        return url


if __name__=='__main__':
    s = S3('main')
    dirpath = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(dirpath, 'data/base.jpg')
    destination = 'ccd_test2.jpg'
    s.upload_file(filename, destination)