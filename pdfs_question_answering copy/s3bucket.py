import boto3
import pandas
# Creating the low level functional client
client = boto3.client(
    's3',
    aws_access_key_id = '',
    aws_secret_access_key = '',
    region_name = ''
)
    
# Creating the high level object oriented interface
resource = boto3.resource(
    's3',
    aws_access_key_id = '',
    aws_secret_access_key = '',
    region_name = ''
)

# Fetch the list of existing buckets
clientResponse = client.list_buckets()
    
# Print the bucket names one by one
print('Printing bucket names...')
for bucket in clientResponse['Buckets']:
    print(f'Bucket Name: {bucket["Name"]}')
