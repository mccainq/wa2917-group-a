from __future__ import print_function

import boto3
import json

dynmoDB = boto3.resource('dynamodb')
cmprhnd_client = boto3.client('comprehend')
tweet_table = dynmoDB.Table('TweetStreamTable')
    
def lambda_handler(event, context):
    print('Procesing records from DynamoDB Stream .....')
    
    try:
        for record in event['Records']:
            print(record['eventName'])
            if record['eventName'] in ['MODIFY', 'INSERT']:
                #print(json.dumps(record['dynamodb']['NewImage']['tweetText']['S']))
                #print(record['dynamodb']['NewImage']['tweetText']['S'])

                # AWS comprehebd Sentimental anlysis..
                sentiment_rslt = cmprhnd_client.detect_sentiment(
                    Text = record['dynamodb']['NewImage']['tweetText']['S'],
                    LanguageCode = 'en'
                    )
                    
                #Update the DyanmoDB tablew ith Sentiment result
                response = tweet_table.update_item(
                    Key={'tweetID': record['dynamodb']['NewImage']['tweetID']['S']},
                    UpdateExpression="set sentiment = :vall ,sentiment_score = :val2",
                    ExpressionAttributeValues={
                        ":vall": sentiment_rslt['Sentiment'],
                        ":val2": str(sentiment_rslt['SentimentScore'])})

        print('Successfully processed records from DynamoDB Stream..')              
    except Exception as e:
        print(e)
        print('Error while procesing records.')
        raise e
    
