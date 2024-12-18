
import boto3
import datetime

aws_id = ''
aws_key = ''
region = ''
key = 'Owner'
value = 'AWS'

def get_account_id():
    sts_client = boto3.client('sts')
    identity = sts_client.get_caller_identity()
    return identity['Account']

# Return a list of ec2 arns
def get_ec2_arns():
  ec2_client = boto3.client("ec2")
  instances = []
  response = ec2_client.describe_instances()
  for reservation in response.get('Reservations', []):
      for instance in reservation.get('Instances', []):
          arn = f"arn:aws:ec2:{instance['Placement']['AvailabilityZone'][:-1]}:{get_account_id()}:instance/{instance['InstanceId']}"
          instances.append(arn)
  return instances

def get_all_arns():
  tagging_client = boto3.client('resourcegroupstaggingapi')
  arn_list=[]
  pag_token=''

  while True:
    response = tagging_client.get_resources(
        PaginationToken=pag_token,
        ResourcesPerPage=100)
    pag_token=response.get('PaginationToken',[])

    taggable_arn_list=response['ResourceTagMappingList']
    for taggable in taggable_arn_list:
      arn_list.append(taggable['ResourceARN'])

    if len(pag_token) > 5:
        response = tagging_client.get_resources(
        PaginationToken=pag_token,
        ResourcesPerPage=1)  
        taggable_arn_list=response['ResourceTagMappingList']
        for taggable in taggable_arn_list:
          arn_list.append(taggable['ResourceARN'])
        pag_token=response.get('PaginationToken',[])
    else:
      break
  return arn_list




# Tag Resource based on ARN
def tag_resources():
  tagging_client = boto3.client('resourcegroupstaggingapi')
  response = tagging_client.tag_resources(
        ResourceARNList=get_ec2_arns()+get_all_arns(),
        Tags={
          key: value
      }
  )

def main():
  tag_resources()

if __name__ == "__main__":
  main()

