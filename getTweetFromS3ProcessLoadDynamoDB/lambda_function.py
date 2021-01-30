
from __future__ import print_function

import json
import boto3
import urllib.parse

s3 = boto3.client('s3')
dynmoDB = boto3.resource('dynamodb')
tweet_table = dynmoDB.Table('TweetStreamTable')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    for record in event['Records']:
        try:
            # Get the object from the event and show its content type
            bucket = record['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
            response = s3.get_object(Bucket=bucket, Key=key)
        
            print('Processing new file, {} from bucket, {}'.format(key, bucket))
            
            tweets = json.loads(response['Body'].read())
            with tweet_table.batch_writer() as batch:
                for tweet in tweets['data']:
                    batch.put_item(
                        Item={
                            'tweetID':tweet['id'],
                            'tweetUserName':tweets['query'],
                            'tweetTS':tweet['created_at'],
                            'tweetText':tweet['text'],
                            'tweetLang':tweet['lang'],
                            'tweetSource':tweet['source']            
                        }
                    )
            print('Process completed  Successfully....')

        except Exception as e:
            print(e)
            print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
            raise e