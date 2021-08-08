from lambda_decorators import json_http_resp, load_json_body
from botocore.exceptions import ClientError
import boto3
import os
import logging

dynamodb = boto3.resource("dynamodb")


@json_http_resp
@load_json_body
def handler(event, context):
    print(event)
    try:
        id = event["pathParameters"]["blob_id"]

        table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])
        response = table.get_item(Key={"id": id})
        return {"statusCode": 200, "body": build_response(response["Item"])}
    except Exception as e:
        logging.error(e)
        return {"statusCode": 404, "body": {"error_message": "Image was not found"}}


def build_response(item):
    if item["labelled"]:
        return {
            "id": item["id"],
            "labelled": item["labelled"],
            "label": item["label"],
        }
    elif "err" in item:
        return {
            "id": item["id"],
            "error": item["err"],
            "error_message": item["error_message"],
        }
    else:
        return {
            "id": item["id"],
            "labelled": item["labelled"],
        }
