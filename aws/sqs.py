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
        Args:
            toAWS (str): name of the queue to use to write to. must be a string that ends in '.fifo'.
            fromAWS (str): name of the queue to use to read from. must be a string that ends in '.fifo'.
        """

        self.fromAWSName = fromAWSName
        self.toAWSName = toAWSName

        self.fromAWSAttributes = {
            'FifoQueue': 'true',
            'DelaySeconds': '0',
            'MessageRetentionPeriod': '180', # 3 minutes before state becomes stale, else deleted.
            'ContentBasedDeduplication': 'true'
        }
        self.toAWSAttributes = {
            'FifoQueue': 'true',
            'DelaySeconds': '0',
            'MessageRetentionPeriod': '900', # 15 minutes to complete a command, else deleted.
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

    def send_status_update(self, status_string):
        """
        Sends a status string (presumably json) to sqs. 

        This doesn't work so well because queues don't support easy 
        retrieval of the most recent entry, which is all we care about.
        
        Currently, this method is unused, but I'm keeping it for reference.
        """
        response = self.sqs_c.send_message(
            QueueUrl=self.toAWS.url,
            MessageBody=status_string,
            MessageGroupId="status_messagegroupid"
        )

    def read_queue_item(self):
        """
        Read one entry in the queue. 
        If successful, return the message body and delete the entry in sqs.
        If unsuccessful (ie. queue is empty), return False.
        """
    
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
            # receipt_handle is used to delete the entry from the queue.
            receipt_handle = message['ReceiptHandle']
            print(f"{message['Body']} was received.\n")
            delete_response = self.sqs_c.delete_message(QueueUrl=self.fromQURL, ReceiptHandle=receipt_handle)
            return message['Body']
        except:
            return False

    def read_queue(self):
        """
        Read all queue entries and return them in a list.

        All messages downloaded at once, then processed sequentially from there.
        For our use, it's better to read and process one at a time (see read_queue_item above)
        
        Currently, this method is not used, but I'm keeping it for reference.
        """
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
                 
                for index in range(length):
                    message = response['Messages'][index]
                    receipt_handle = message['ReceiptHandle']
                    messages.append(message['Body'])
                    self.sqs_c.delete_message(QueueUrl=self.fromQURL, ReceiptHandle=receipt_handle)
            except:
                continue
            break
        #print(f"\nNumber of messages: {len(messages)}")
        #print('Messages: ', *messages, sep='\n- ')
        return messages

    def send_to_queue(self, messageBody="empty body"):
        """
        Send a message to the 'toAWS' queue.
        Args:
            messagebody (str): body of the message to send.
        """

        # Arbitrary string. Not exactly sure what this does.
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

        SQS class is not a great place for this method, but I won't mess with
        things unless we start using this code for real.
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