import boto3
import os

# Inicializar clientes de AWS
dynamodb = boto3.resource('dynamodb')

# Variables de entorno para las tablas DynamoDB
PRODUCTS_TABLE_NAME = os.environ['PRODUCTS_TABLE_NAME']

def lambda_handler(event, context):
    products_table = dynamodb.Table(PRODUCTS_TABLE_NAME)

    for record in event['Records']:
        message = record['body']
        product_id, tenant_id, category, action = message.split(':')

        if action == 'Restock needed':
            products_table.update_item(
                Key={
                    'ProductId': product_id,
                    'TenantId': tenant_id
                },
                UpdateExpression='SET Stock = :val',
                ExpressionAttributeValues={
                    ':val': 25  # Se puede ajustar según las necesidades
                }
            )

    return {
        'statusCode': 200,
        'body': 'Inventory updated successfully'
    }
