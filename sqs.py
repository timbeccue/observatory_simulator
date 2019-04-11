# sqs_send.py

import boto3
import json
import random
from tqdm import tqdm # progress bars
import sys

class Queuer():

    sqs_r = boto3.resource('sqs', 'us-east-1')
    sqs_c = boto3.client('sqs', 'us-east-1')

    def __init__(self, toAWS="to_aws_pythonbits.fifo", fromAWS="from_aws_pythonbits.fifo"):
        """
        Get an existing sqs queue, or create a new one if the requested queue doesn't exist.
        :param toAWS: name of the queue to use to write to. must be a string that ends in '.fifo'.
        :param fromAWS: name of the queue to use to read from. must be a string that ends in '.fifo'.
        """

        self.toAWSName = toAWS
        self.fromAWSName = fromAWS
        self.queueCreateAttributes = {
            'FifoQueue': 'true',
            'DelaySeconds': '0',
            'MessageRetentionPeriod': '1800',
            'ContentBasedDeduplication': 'true'
        }


        # Get the queue that we write to, if it already exists
        # If it doesn't exist already, create it.
        try: 
            self.toAWS = self.sqs_r.get_queue_by_name(QueueName=self.toAWSName)
            #print(f'Using existing queue: {self.toAWS.url}')
        except:
            self.toAWS = self.sqs_r.create_queue(QueueName=self.toAWSName, Attributes=self.queueCreateAttributes)
            #print(f'Created new queue: {self.toAWS.url}')


        # Get the queue that we read from, if it already exists
        # If it doesn't exist already, create it.
        try: 
            self.fromAWS = self.sqs_r.get_queue_by_name(QueueName=self.fromAWSName)
            #print(f'Using existing queue: {self.fromAWS.url}')
        except:
            self.fromAWS = self.sqs_r.create_queue(QueueName=self.fromAWSName, Attributes=self.queueCreateAttributes)
            #print(f'Created new queue: {self.fromAWS.url}')

        self.fromQURL = self.fromAWS.url
        self.toQURL = self.toAWS.url


    def read_queue(self):
        messages = []
        while True:
    
            response = self.sqs_c.receive_message(
                QueueUrl=self.fromQURL,
                AttributeNames=[ 'device' ],
                MaxNumberOfMessages=10,    
                MessageAttributeNames=[ 'All' ],
                VisibilityTimeout=10,         #This CANNOT BE 0!  
                WaitTimeSeconds=3 # 0==short polling, 0<x<20==long polling
            )
        
            try:
                length = -1
                length = len(response['Messages'])
                 
                print('\n', length, ' messages in to_WMD_1 queue. ', end="")
                for index in range(length):
                    message = response['Messages'][index]
                    receipt_handle = message['ReceiptHandle']
                    #print(f"{message['Body']} was received.\n")
                    messages.append(message['Body'])
                    delete_response = self.sqs_c.delete_message(QueueUrl=self.fromQURL, ReceiptHandle=receipt_handle)
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    #continue
            except:
                continue
                print('\nto_WMD_1 queue is empty.\n')
                break  #Just to end this little demo 
            break
        #print(f"\nNumber of messages: {len(messages)}")
        #print('Messages: ', *messages, sep='\n- ')
        return messages

    def send_to_queue(self, messageBody="It was a modest afternoon..."):
        messageAttributes = {
            "Title": {
                "DataType": "String",
                "StringValue": "Margaret\"s big adventure"
            },
            "AnotherAttribute": {
                "DataType": "String",
                "StringValue": "Another string value"
            },
        }
        messageGroupId = 'LandOfSunshine'
        mountCommand = json.dumps({
            "device":  f"mount_{random.randint(0,9)}",
            "equinox":  2000.0,
            #"ra": "12h30m30.0s",
            "ra": round(random.random() * 24, 3),
            #"ha_rate":  0.1E-5,
            "dec": round(random.random() * 180 - 90, 3),
            "tracking":  True,  
            "command": "goto",
            "messagebody": messageBody
        })

        response = self.sqs_c.send_message(
            QueueUrl=self.fromAWS.url,
            #MessageAttributes=messageAttributes,
            MessageBody=mountCommand,
            MessageGroupId=messageGroupId,
            #MessageDeduplicationId=str(randy)
        )
        #print(f"Sent message. Message id is {response['MessageId']}")

    def send(self,n):
        def test_msg(i=0):
            while True:
                yield f"test message {i}"
                i += 1
        msg = test_msg()
        for k in tqdm(range(n), ncols=100):
            self.send_to_queue(next(msg))



if __name__=="__main__":
    q = Queuer()
    q.read_queue()
    #q.send_to_queue()