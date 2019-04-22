import boto3
import os
from botocore.client import Config


class S3:

    # Get the service client with sigv4 configured
    s3_c = boto3.client('s3', 'us-east-1', config=Config(signature_version='s3v4'))

    # The name of the bucket used by this class instance.
    bucket_name = 'pythonbits'

    def __init__(self, site_name):

        self.bucket = self.s3_c.create_bucket(Bucket=self.bucket_name)
        self.site_name = site_name

    def upload_file(self, to_filename):
        """
        This method uploads a file to s3.

        Instead of an actual result, we have a hardcoded test image path to a jpg.

        Args:
            to_filename (str): the file's name in s3. Doesn't include save directory.

        """
        # Hardcoded test image we're pretending to be the actual data.
        from_file = '../data/base.jpg'
        dirpath = os.path.abspath(os.path.dirname(__file__))
        from_filename = os.path.join(dirpath, from_file)

        # Add the path to the directory where the file will be saved.
        to_file = f'{self.site_name}/'+to_filename

        try:
            response = self.s3_c.upload_file(
                Filename=from_filename, 
                Bucket=self.bucket_name, 
                Key=to_file,
                ExtraArgs={
                    # Allow creation of links that don't require credentials.
                    'ACL':'public-read',
                    # This makes a browser open the image in a tab, 
                    # rather than download the file.
                    'ContentType': 'image/jpg'
                    }
                )    

            print("file upload success")
        except Exception as e:
            print(f"error uploading to s3: {e}")

    def get_image_url(self, filename):
        """
        Generate a publicly-accessible url to the image named <filename>.

        The save directory is assumed to be the folder corresponding to the
        site that is associated with the running instance of this class.
        """
        params = {
            'Bucket': str(self.bucket_name),
            # Key = folder path + filename
            'Key': f'{self.site_name}/'+str(filename)
        }
        url = self.s3_c.generate_presigned_url(
            ClientMethod='get_object', 
            Params=params,
            ExpiresIn=3600 # URL expires in 1 hour.
        )
        return url


if __name__=='__main__':
    s = S3('main')
    dirpath = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(dirpath, 'data/base.jpg')
    destination = 'ccd_test2.jpg'
    s.upload_file(destination)