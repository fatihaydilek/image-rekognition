from lambda_decorators import json_http_resp, load_json_body
import boto3
import logging
import os
import time
import json
import botocore
import logging

rekognition_client=boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

@json_http_resp
@load_json_body
def handler(event, context):
    records = event.get("Records")
    for record in records:
        try:
            bucket = record['s3']['bucket']['name']
            photo = record['s3']['object']['key']

            response = rekognition_client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                MaxLabels=10)

            print("label1", response['Labels'])
            print("label2", json.dumps(response['Labels']))

            printLabelDetails(response, photo)
            update_image_metadata(photo, response)

            result = {
                "id": photo,
                "labels": response['Labels'],
            }
            return result

        except botocore.exceptions.ClientError as error:
            print("botocore.exceptions.ClientError", error)
            if error.response['Error']['Code'] == 'InvalidImageFormatException':
                logging.warn('Invalid image format')
                update_image_error_status(photo)
            else:
                raise error


def printLabelDetails(response, photo):
    print('Detected labels for ' + photo) 
    print()   
    for label in response['Labels']:
        print ("Label: " + label['Name'])
        print ("Confidence: " + str(label['Confidence']))
        print ("Instances:")
        for instance in label['Instances']:
            print ("  Bounding box")
            print ("    Top: " + str(instance['BoundingBox']['Top']))
            print ("    Left: " + str(instance['BoundingBox']['Left']))
            print ("    Width: " +  str(instance['BoundingBox']['Width']))
            print ("    Height: " +  str(instance['BoundingBox']['Height']))
            print ("  Confidence: " + str(instance['Confidence']))
            print()

        print ("Parents:")
        for parent in label['Parents']:
            print ("   " + parent['Name'])
        print ("----------")
        print ()

def update_image_metadata(id, response):
    try:
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

        timestamp = str(time.time())
        table.update_item(
            Key={
                'id': id,
            },
            UpdateExpression="set labelled=:p, updatedAt=:u, label=:l",
            ExpressionAttributeValues={
                ':p': True,
                ':u': timestamp,
                ':l': json.dumps(response['Labels'])

            },
            ReturnValues="UPDATED_NEW"
        )
    except botocore.exceptions.ClientError as error:
        logging.error(error)
        raise error



def update_image_error_status(id):
    try:
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

        timestamp = str(time.time())
        table.update_item(
            Key={
                'id': id,
            },
            UpdateExpression="set err=:e, error_message=:m, updatedAt=:u",
            ExpressionAttributeValues={
                ':e': True,
                ':m': "Invalid file format",
                ':u': timestamp,
            },
            ReturnValues="UPDATED_NEW"
        )
    except botocore.exceptions.ClientError as error:
        logging.error(error)
        raise error