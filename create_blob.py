from service.s3_service import create_presigned_post
import json
import os
import logging
import time
import uuid
import validators

import boto3

dynamodb = boto3.resource("dynamodb")


def handler(event, context):

    callback_url = ""
    data = json.loads(event["body"])
    if "callback_url" in data:
        print("callback_url", data["callback_url"])
        if validators.url(data["callback_url"]):
            callback_url = data["callback_url"]
        else:
            return {
                "statusCode": 400,
                "body": {"errorMessage": "Callback url is not valid"},
            }

    blob_id = uuid.uuid4().hex
    presigned_url = create_presigned_post(os.environ["BUCKET_NAME"], blob_id)

    if presigned_url is None:
        logging.error("Error while generating signed url")
        return {"statusCode": 503, "body": {"errorMessage": "Service Unavailable"}}

    save_blob(blob_id, callback_url)

    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(
            {
                "id": blob_id,
                "presigned_url": presigned_url,
            }
        ),
    }

    return response


def save_blob(blob_id, callback_url):
    timestamp = str(time.time())
    table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])
    item = {
        "id": blob_id,
        "callbackUrl": callback_url,
        "labelled": False,
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }

    table.put_item(Item=item)
