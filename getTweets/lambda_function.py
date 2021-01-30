import json
import boto3
import urllib3

# get twitter bearer for API call
def get_auth():
  ssm_client=boto3.client('ssm', region_name="us-east-1")
  return ssm_client.get_parameter(Name="twitter_bearer")

# query twitter from user import
def get_response(user_query):
  auth=get_auth()
  http = urllib3.PoolManager()
  headers = {"Authorization": f'Bearer {auth["Parameter"]["Value"]}'}
  tweet_fields="tweet.fields=author_id,geo,lang,source,entities,possibly_sensitive,created_at"
  user_fields="user.fields=name,location,created_at,username"
  query=f"from:{user_query} -is:retweet"
  url=f"https://api.twitter.com/2/tweets/search/recent?query={query}&{tweet_fields}&{user_fields}&max_results=100"
  return http.request("GET", url, headers=headers)

# saves json to s3 bucket
def save_to_s3(response):
  s3_resource=boto3.resource("s3")
  s3object=s3_resource.Object("sentiment-analysis-g1", "query_results.json")
  s3object.put(
    Body=(bytes(json.dumps(response, indent=4).encode("UTF-8")))
  )
  
# ensure test lambda key/value is {"query": "input username here"}
def lambda_handler(event, context):
  response=get_response(event["query"])
  save_to_s3(json.loads(response.data))