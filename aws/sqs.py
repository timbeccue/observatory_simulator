# sqs_send.py

import boto3
from tqdm import tqdm # progress bars
import sys,time,random,json

class Queuer():

    sqs_r = boto3.resource('sqs', 'us-east-1')
    sqs_c = boto3.client('sqs', 'us-east-1')

    def __init__(self, fromAWSName, toAWSName):
        """
        Get an existing sqs queue, or create a new one if the requested queue doesn't exist.
        :param toAWS: name of the queue to use to write to. must be a string that ends in '.fifo'.
        :param fromAWS: name of the queue to use to read from. must be a string that ends in '.fifo'.
        """

        #self.fromAWSName = "to_aws_pythonbits.fifo" 
        #self.toAWSName = "from_aws_pythonbits.fifo"
        self.fromAWSName = fromAWSName
        self.toAWSName = toAWSName

        self.fromAWSAttributes = {
            'FifoQueue': 'true',
            'DelaySeconds': '0',
            'MessageRetentionPeriod': '180', # 3 minutes before state becomes stale
            'ContentBasedDeduplication': 'true'
        }
        self.toAWSAttributes = {
            'FifoQueue': 'true',
            'DelaySeconds': '0',
            'MessageRetentionPeriod': '900', # 15 minutes to complete a command
            'ContentBasedDeduplication': 'true'
        }


        # Get the queue that we write to, if it already exists
        # If it doesn't exist already, create it.
        try: 
            self.toAWS = self.sqs_r.get_queue_by_name(QueueName=self.toAWSName)
            #print(f'Using existing queue: {self.toAWS.url}')
        except:
            self.toAWS = self.sqs_r.create_queue(QueueName=self.toAWSName, Attributes=self.toAWSAttributes)
            #print(f'Created new queue: {self.toAWS.url}')


        # Get the queue that we read from, if it already exists
        # If it doesn't exist already, create it.
        try: 
            self.fromAWS = self.sqs_r.get_queue_by_name(QueueName=self.fromAWSName)
            #print(f'Using existing queue: {self.fromAWS.url}')
        except:
            self.fromAWS = self.sqs_r.create_queue(QueueName=self.fromAWSName, Attributes=self.fromAWSAttributes)
            #print(f'Created new queue: {self.fromAWS.url}')

        self.fromQURL = self.fromAWS.url
        self.toQURL = self.toAWS.url


    def read_queue_item(self):
    
        response = self.sqs_c.receive_message(
            QueueUrl=self.fromQURL,
            #AttributeNames=[ 'device' ],
            MaxNumberOfMessages=1,    
            #MessageAttributeNames=[ 'All' ],
            VisibilityTimeout=10,         #This CANNOT BE 0!  
            WaitTimeSeconds=3 # 0==short polling, 0<x<20==long polling
        )
        try:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            print(f"{message['Body']} was received.\n")
            delete_response = self.sqs_c.delete_message(QueueUrl=self.fromQURL, ReceiptHandle=receipt_handle)
            return message['Body']
        except:
            return False

    def send_status_update(self, status_string):
        response = self.sqs_c.send_message(
            QueueUrl=self.toAWS.url,
            MessageBody=status_string,
            MessageGroupId="status_messagegroupid"
        )

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
                 
                #print('\n', length, ' messages in to_WMD_1 queue. ', end="")
                for index in range(length):
                    message = response['Messages'][index]
                    receipt_handle = message['ReceiptHandle']
                    #print(f"{message['Body']} was received.\n")
                    messages.append(message['Body'])
                    self.sqs_c.delete_message(QueueUrl=self.fromQURL, ReceiptHandle=receipt_handle)
                    #sys.stdout.write('.')
                    #sys.stdout.flush()
                    #print()
                    #continue
            except:
                continue
            break
        #print(f"\nNumber of messages: {len(messages)}")
        #print('Messages: ', *messages, sep='\n- ')
        return messages

    def send_to_queue(self, messageBody="empty body"):
        messageGroupId = 'LandOfSunshine'

        response = self.sqs_c.send_message(
            QueueUrl=self.fromAWS.url,
            MessageBody=messageBody,
            MessageGroupId=messageGroupId,
        )
        #print(f"Sent message. Message id is {response['MessageId']}")


    def send(self,n):
        """ 
        Send n test messages to goto random ra and dec.
        """
        def test_msg(i=0):
            while True:
                yield json.dumps({
                    "device": "mount_1",
                    "ra": round(random.random() * 24, 3),
                    "dec": round(random.random() * 180 - 90, 3),
                    "command": "goto",
                    "timestamp": int(time.time()),
                    "test id": i,
                })
                i += 1
        msg = test_msg()
        for k in tqdm(range(n), ncols=70):
            self.send_to_queue(next(msg))



if __name__=="__main__":
    pass
    #q = Queuer()
    #q.read_queue()
    #q.send_to_queue()