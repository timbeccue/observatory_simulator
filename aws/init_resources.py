# resources.py

from aws import sqs, dynamodb, s3
import yaml

class Resources:
    """ 
    Initialize resources for all the sites listed in the config file.
    
    Args:
        configfile (str): path to the yaml configuration file.

    """

    @staticmethod
    def make_sqs(sitename):
        """
        Initialize the sqs helper class instance for a given site.

        Args:
            sitename (str): name used for the queuenames and internal methods 
                            of the sqs class instance.
        Returns: 
            sqs class instance (defined in aws/sqs.py)
        """
        fromAWS = sitename + '_from_aws_pythonbits.fifo'
        toAWS = sitename + '_to_aws_pythonbits.fifo'
        return sqs.Queuer(fromAWS, toAWS)

    @staticmethod
    def make_dynamodb(sitename):
        """
        Initialize and return a dynamodb table class instance for a given site.

        Args:
            sitename (str): name used for the table name and internal methods 
                            of the dynamodb class instance.
        Returns: 
            dynamodb class instance (defined in aws/dynamodb.py)
        """
        tablename = sitename + "_state_pythonbits"
        return dynamodb.DynamoDB(tablename) 

    @staticmethod
    def make_s3(sitename):
        """
        Initialize and return an s3 helper class instance for a given site.

        Args:
            sitename (str): name used for the directory name and internal methods 
                            of the s3 class instance.
        Returns: 
            s3 class instance (defined in aws/s3.py)
        """
        return s3.S3(sitename)


    def __init__(self, configfile):
        """
        Create resources for each site in the configfile, saving the 
        results in a list for each resource type. 

        These lists can be accessed with the getter methods below.

        Args:
            configfile (str): path to the yaml configuration file.
        
        """

        self.all_sqs = {}
        self.all_dynamodb = {}
        self.all_s3 = {}
        self.all_sites = []

        with open(configfile, 'r') as stream:
            try: 
                self.config = yaml.safe_load(stream)
                self.all_sites = list(self.config['Sites'].keys())

                for site in self.all_sites:
                    self.all_sqs[site] = self.make_sqs(site)
                    self.all_dynamodb[site] = self.make_dynamodb(site)
                    self.all_s3[site] = self.make_s3(site)
            
            except Exception as e:
                print(f"Exception: {e}")


    def get_all_sites(self):
        return self.all_sites

    def get_all_sqs(self):
        return self.all_sqs

    def get_all_dynamodb(self):
        return self.all_dynamodb

    def get_all_s3(self):
        return self.all_s3