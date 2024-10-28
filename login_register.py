import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', 
    aws_access_key_id='YOUR_ACCESS_KEY', 
    aws_secret_access_key='YOUR_SECRET_KEY', 
    region_name='us-east-1'
)
user_table = dynamodb.Table('User')

def check_login(username, password):
    try:
        response = user_table.get_item(Key={'Name': username, 'Password': password})
        if 'Item' in response:
            return response['Item']['Role']
        else:
            return None
    except Exception as e:
        print(f"Error checking login: {e}")
        return None

def register_user(username, password, role):
    try:
        user_table.put_item(Item={
            'Name': username,
            'Password': password,
            'Role': role
        })
        print("User registered successfully!")
    except Exception as e:
        print(f"Error registering user: {e}")
