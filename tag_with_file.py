import boto3
from datetime import datetime

view_arn = 'arn:aws:resource-explorer-2:us-east-1:339712936044:view/all-resources/4045031f-8521-4e19-aa03-c62da348fe7a'
ec2_filter = 'service:ec2'
s3_filter = 'service:s3'
region_filter = 'region:us-east-1'
file_path = 'tags.txt'

# Return tags from file
def read_tag_file(path):
  tags = {}
  with open(path, "r") as file:
    for line in file:
      line = line.strip()
      if line and '=' in line:
        key, value = line.split("=",1)
        tags[key.strip()] = value.strip()
  return tags

# Display timestamp
def log_message():
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  return timestamp

def get_all_res_arns(view, region):
  client = boto3.client('resource-explorer-2')
  arn_list = []
  next_token = None
  # filters = {'FilterString': region_filter+' '+s3_filter}
  filters = {'FilterString': 'region'+':'+region}
  # filters = None

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

# Get all regions
def get_all_regions():
  regions = []
  client = boto3.client("ec2")
  response = client.describe_regions(AllRegions=True)
  regions.extend(res['RegionName'] for res in response.get('Regions', []))
  return regions

# Tag Resource based on ARN and Region
def tag_resources_from_file():
  try:
    tags = read_tag_file(file_path)
    if tags == {}:
      print(f"{log_message()} -- No tags in provided file!")
      return
    all_regions = get_all_regions()
    all_res = []
    for region in all_regions:
      all_res = get_all_res_arns(view_arn, region)
      if len(all_res) == 0:
        continue
      tagging_client = boto3.client('resourcegroupstaggingapi', region_name=region) if region else boto3.client("resourcegroupstaggingapi")
      for arn in all_res:
        try:
          response = tagging_client.tag_resources(
            ResourceARNList=[arn],
            Tags=tags)
          print(f"{log_message()} -- Successfully tagged: {arn}")
        except Exception as e:
          print(f"{log_message()} -- Failed to tag {arn}. Error: {e}")

  except Exception as e:
    print(f"Error {e}")

def main(): 
  tag_resources_from_file()

if __name__ == "__main__":
  main()
  # pass
