import boto3
import os
from random import randint

# Inicializar clientes de AWS
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Variables de entorno para las tablas DynamoDB y el SNS Topic
PRODUCTS_TABLE_NAME = os.environ['PRODUCTS_TABLE_NAME']
PRODUCTS_FREQUENT_TABLE_NAME = os.environ['PRODUCTS_FREQUENT_TABLE_NAME']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    products_table = dynamodb.Table(PRODUCTS_TABLE_NAME)
    products_frequent_table = dynamodb.Table(PRODUCTS_FREQUENT_TABLE_NAME)

    response = products_table.scan()

    for item in response['Items']:
        if item['Stock'] == 0:
            # Actualizar la tabla de productos frecuentes
            response_frequent = products_frequent_table.get_item(
                Key={
                    'ProductId': item['ProductId'],
                    'TenantId': item['TenantId']
                }
            )
            if 'Item' in response_frequent:
                frequency = response_frequent['Item']['Frequency'] + 1
                products_frequent_table.update_item(
                    Key={
                        'ProductId': item['ProductId'],
                        'TenantId': item['TenantId']
                    },
                    UpdateExpression='SET Frequency = :val',
                    ExpressionAttributeValues={
                        ':val': frequency
                    }
                )
            else:
                products_frequent_table.put_item(
                    Item={
                        'ProductId': item['ProductId'],
                        'TenantId': item['TenantId'],
                        'Frequency': 1
                    }
                )
            # Enviar mensaje a la cola SQS
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=f"{item['ProductId']}:{item['TenantId']}:{item['Category']}:Restock needed"
            )

            # Restablecer el stock del producto
            new_stock = randint(20, 30)
            products_table.update_item(
                Key={
                    'ProductId': item['ProductId'],
                    'TenantId': item['TenantId']
                },
                UpdateExpression='SET Stock = :val',
                ExpressionAttributeValues={
                    ':val': new_stock
                }
            )

    return {
        'statusCode': 200,
        'body': 'Inventory checked and updated successfully'
    }
