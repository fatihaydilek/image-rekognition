from lambda_decorators import json_http_resp, load_json_body

# import requests


@json_http_resp
@load_json_body
def handler(event, context):
    print("event", event["Records"])
    for record in event["Records"]:
        if record["eventName"] == "MODIFY":
            callback_url = record["dynamodb"]["NewImage"]["callbackUrl"]["S"]
            item = build_callback_data(record)

            print("Make req", item)
            # http_response = requests.post(callback_url, data=item)
            # if http_response.status_code != 200:
            #     print("Retry !")


def build_callback_data(record):
    if "err" in record["dynamodb"]["NewImage"]:
        return {
            "id": record["dynamodb"]["Keys"]["id"]["S"],
            "error": record["dynamodb"]["NewImage"]["err"]["BOOL"],
            "error_message": record["dynamodb"]["NewImage"]["error_message"]["S"],
        }
    else:
        return {
            "id": record["dynamodb"]["Keys"]["id"]["S"],
            "label": record["dynamodb"]["NewImage"]["label"]["S"],
        }
