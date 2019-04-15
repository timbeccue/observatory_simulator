# dynamodb.py

import boto3, time

class DynamoDB():

    d = boto3.resource('dynamodb', 'us-east-1')

    def __init__(self, tablename):
        
        self.table_name = tablename #"observatory_state_pythonbits"
        self.hash_name = "State"

        # Try creating table. If table already exists, use existing.
        try: 
            self.table = self.create_table(self.table_name, self.hash_name)
            #print(f'Created new table: {self.table}.')
        except Exception as e:
            self.table = self.d.Table(self.table_name) 
            #print(f'Using existing table: {self.table}.')


    def create_table(
        self, table_name, hash_name,
        read_throughput=5, write_throughput=5
    ):
        dynamodb = self.d

        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': hash_name,
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': hash_name,
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': read_throughput,
                'WriteCapacityUnits': write_throughput
            }
        )
        if table:
            print("Success !")
        return table

    def insert_item(self, item, ttl=300):
        """
        Insert item into database.
        Item must be of type dict, and contain the primary key/value.
        """
        response = self.table.put_item(Item=item)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def get_item(self, item):
        """
        Get an item from dynamodb.
        @param item dict must contain primary key, and value of target entry.
        """
        response = self.table.get_item(Key=item)
        item = response['Item']
        return item




if __name__=="__main__":
    d = DynamoDB();

    #item = {
    #    "State": "stateval",
    #    "key1": "val1",
    #    "key2": str(time.time())
    #}
    #item2 = {
    #    "State": "anotherstate",
    #    "key2": str(time.time()*2),
    #    "key3": "thirdval" 
    #}
    #print(d.insert_item(item))
    #print(d.insert_item(item2))
    #print(d.get_item({"State": "anotherstate"}))