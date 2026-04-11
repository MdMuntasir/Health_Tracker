import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
from app.config import AWS_REGION, TABLE_NAME

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

def get_table():
    return dynamodb.Table(TABLE_NAME)

def _floats_to_decimals(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _floats_to_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_floats_to_decimals(v) for v in obj]
    return obj

def put_item(item):
    get_table().put_item(Item=_floats_to_decimals(item))

def get_item(user_id, sk):
    response = get_table().get_item(Key={"user_id": user_id, "sk": sk})
    return response.get("Item")

def query_items(user_id, sk_prefix):
    response = get_table().query(
        KeyConditionExpression=Key("user_id").eq(user_id) & Key("sk").begins_with(sk_prefix)
    )
    return response.get("Items", [])

def delete_item(user_id, sk):
    get_table().delete_item(Key={"user_id": user_id, "sk": sk})

def update_item(user_id, sk, update_expression, expression_values):
    get_table().update_item(
        Key={"user_id": user_id, "sk": sk},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
    )

def get_user_by_email(email):
    response = get_table().scan(
        FilterExpression=Attr("sk").eq("PROFILE") & Attr("email").eq(email)
    )
    items = response.get("Items", [])
    return items[0] if items else None
