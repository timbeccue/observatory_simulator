# delete_site.py

"""

Delete resources at AWS associated with a site. This includes:
 - S3 directory with images
 - SQS to/from queues
 - DynamoDB table that holds observatory status

This script is run directly from the command line, with the site name
as the only argument:

>>> python delete_site.py <sitename>

"""
import sys, boto3


# This is the name of the s3 bucket, and used in sqs/dynamodb names too.
resource_name = 'pythonbits'
resource_region = 'us-east-1'


def ask_user(question):
    check = str(input(f"{question} (Yes/no): ")).lower().strip()
    try:
        if check[0] == 'y':
            return True
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return ask_user(question)
    except:
        print("Please enter a valid input")
        return ask_user(question)

def delete_resources(sitename):

    # Remove s3 folder
    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(resource_name)
        bucket.objects.filter(Prefix=sitename+'/').delete()
        print("S3 directory deleted.")
    except:
        print("No s3 folder to delete.")

    # Remove sqs queues
    try:
        sqs_r = boto3.resource('sqs', resource_region)
        sqs_c = boto3.client('sqs', resource_region)
        fromAWS = sitename + '_from_aws_pythonbits.fifo'
        toAWS = sitename + '_to_aws_pythonbits.fifo'
        sqs_c.delete_queue(QueueUrl=sqs_r.get_queue_by_name(QueueName=fromAWS).url)
        sqs_c.delete_queue(QueueUrl=sqs_r.get_queue_by_name(QueueName=toAWS).url)
        print("SQS queues deleted.")
    except:
        print("No sqs queue to delete.")

    # Remove dynamodb table
    try:
        dynamodb = boto3.resource('dynamodb', region_name=resource_region)
        tablename = sitename + "_state_pythonbits"
        table = dynamodb.Table(tablename)
        table.delete()
        print("DynamodDB table deleted.")
    except:
        print("No dynamodb table to delete.")


if __name__=='__main__':

    if len(sys.argv) != 2:
        print("Please add command line argument: sitename")
    else:
        sitename = sys.argv[1]
        confirm_q= f"Are you sure you want to delete all aws resources for {sitename}?"
        confirmation = ask_user(confirm_q)
        if confirmation: 
            delete_resources(sitename)
