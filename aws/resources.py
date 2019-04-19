# resources.py

from aws import sqs, dynamodb, s3
import yaml

class Resources:

    @staticmethod
    def make_sqs(sitename):
        fromAWS = sitename + '_from_aws_pythonbits.fifo'
        toAWS = sitename + '_to_aws_pythonbits.fifo'
        return sqs.Queuer(fromAWS, toAWS)

    @staticmethod
    def make_dynamodb(sitename):
        tablename = sitename + "_state_pythonbits"
        return dynamodb.DynamoDB(tablename) 

    @staticmethod
    def make_s3(sitename):
        return s3.S3(sitename)

    def __init__(self, configfile):

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

    def get_all_dyanmodb(self):
        return self.all_dynamodb

    def get_all_s3(self):
        return self.all_s3