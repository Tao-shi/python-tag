import boto3
import datetime

region = 'us-east-1'
key = 'Owner'
value = 'Tao'
list_keys = [{'key': 'value'}, {'key2': 'value2'}, {'key3': 'value3'}]

# Get aAWS Account ID
def get_account_id():
  sts_client = boto3.client('sts')
  identity = sts_client.get_caller_identity()
  return identity['Account']

# Return a list of ec2 arns
def get_ec2_arns():
  ec2_client = boto3.client("ec2")
  account_id = get_account_id()
  instances_arn = []
  
  try:
    paginator = ec2_client.get_paginator('describe_instances')
    for page in paginator.paginate():
      for reservation in page.get('Reservations', []):
        for instance in reservation.get('Instances', []):
          region = instance['Placement']['AvailabilityZone'][:-1]
          arn = f"arn:aws:ec2:{region}:{account_id}:instance/{instance['InstanceId']}"
          instances_arn.append(arn)
    return instances_arn
  except Exception as e:
    print(f"Error retrieving EC2 ARNs: {e}")
    return []      

# Return a list of all s3 bucket arns
def get_s3_arns():
  s3_client = boto3.client('s3')
  try:
    response = s3_client.list_buckets()
    bucket_arns = []
    
    # Construct ARNs for each bucket
    for bucket in response['Buckets']:
      bucket_name = bucket['Name']
      bucket_arn = f"arn:aws:s3:::{bucket_name}"
      bucket_arns.append(bucket_arn)
    
    return bucket_arns
  except Exception as e:
    print(f"Error retrieving S3 buckets: {e}")
    return []

# Retrieve ARNs of all taggable resources in the account
def get_all_arns():
  tagging_client = boto3.client('resourcegroupstaggingapi')
  arn_list = []
  pagination_token = ''

  try:
    while True:
      response = tagging_client.get_resources(
        PaginationToken=pagination_token,
        ResourcesPerPage=100
      )   
        # Collect ARNs from the current page
      for taggable in response.get('ResourceTagMappingList', []):
        arn_list.append(taggable['ResourceARN'])
          
        # Check for the next pagination token
      pagination_token = response.get('PaginationToken', '')
      if len(pagination_token) < 5 or not pagination_token:  
        break
    return arn_list

  except Exception as e:
      print(f"Error retrieving resources: {e}")
      return []

get_all_arns()

# Tag Resource based on ARN
def tag_resources():
  tagging_client = boto3.client('resourcegroupstaggingapi')
  all_arns = list(dict.fromkeys(get_ec2_arns()+get_all_arns()+get_s3_arns()))
  print(all_arns)
  for arn in all_arns:
    try:
      response = tagging_client.tag_resources(
        ResourceARNList=[arn],
        Tags={
          key: value 
            }
        )
      print(f"Successfully tagged: {arn}")
    except Exception as e:
      print(f"Failed to tag {arn}. Error: {e}")

def main(): 
  tag_resources()

if __name__ == "__main__":
  main()

