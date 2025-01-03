import boto3
from datetime import datetime

region = 'us-east-1'
key = 'Key'
value = 'Test'
view_arn = 'arn:aws:resource-explorer-2:us-east-1:339712936044:view/all-resources/4045031f-8521-4e19-aa03-c62da348fe7a'
ec2_filter = 'service:ec2'
s3_filter = 'service:s3'
region_filter = 'region:us-east-1'
file_path = 'tags.txt'

# Get AWS Account ID
def get_account_id():
  sts_client = boto3.client('sts')
  identity = sts_client.get_caller_identity()
  return identity['Account']

def read_tag_file(path):
  tags = {}
  with open(path, "r") as file:
    for line in file:
      line = line.strip()
      if line and '=' in line:
        key, value = line.split("=",1)
        tags[key.strip()] = value.strip()
  return tags

print(read_tag_file(file_path))

# Display timestamp
def log_message():
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  return timestamp

def get_all_res_arns(view):
  client = boto3.client('resource-explorer-2')
  arn_list = []
  next_token = None
  filters = {'FilterString': region_filter+' '+s3_filter}
  # filters = None

  try:
    while True:
      # Build the request parameters
      params = {'MaxResults': 1000, 'ViewArn': view, 'Filters': filters} if filters else {'MaxResults': 1000, 'ViewArn': view}
      if next_token:
        params['NextToken'] = next_token

      # Fetch resources
      response = client.list_resources(**params)
      arn_list.extend(res['Arn'] for res in response.get('Resources', []))

      # Check for next token
      next_token = response.get('NextToken')
      if not next_token:
        break
    return arn_list

  except Exception as e:
    print(f"Error retrieving resources: {e}")
    return [] 

# Tag Resource based on ARN
def tag_resources():
  tagging_client = boto3.client('resourcegroupstaggingapi', region_name=region) if region else boto3.client("resourcegroupstaggingapi")
  all_arns = list(dict.fromkeys(get_all_res_arns(view_arn)))

  if len(all_arns) == 0 :
    print("No resources found to tag!")
    return
  else:
    for arn in all_arns:
      try:
        response = tagging_client.tag_resources(
          ResourceARNList=[arn],
          Tags={
            key:value
              }
          )
        print(f"{log_message()} -- Successfully tagged: {arn}")
      except Exception as e:
        print(f"{log_message()} -- Failed to tag {arn}. Error: {e}")

def tag_resources_from_file():
  tags = read_tag_file(file_path) if file_path else None
  tagging_client = boto3.client('resourcegroupstaggingapi', region_name=region) if region else boto3.client("resourcegroupstaggingapi")
  all_arns = list(dict.fromkeys(get_all_res_arns(view_arn)))

  if len(all_arns) == 0 :
    print("No resources found to tag!")
    return
  else:
    for arn in all_arns:
      if tags:
        try:
          response = tagging_client.tag_resources(
            ResourceARNList=[arn],
            Tags=tags
            )
          print(f"{log_message()} -- Successfully tagged: {arn}")
        except Exception as e:
          print(f"{log_message()} -- Failed to tag {arn}. Error: {e}")
      else:
        print("No tags in file!")
        return

def main(): 
  # tag_resources()
  tag_resources_from_file()

if __name__ == "__main__":
  main()
  # pass
