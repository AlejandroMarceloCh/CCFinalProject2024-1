import boto3
import os
from botocore.exceptions import ClientError

# Inicializar clientes de AWS
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
textract = boto3.client('textract')

# Variables de entorno para las tablas DynamoDB y el bucket S3
PRODUCTS_TABLE_NAME = os.environ['PRODUCTS_TABLE_NAME']
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

def lambda_handler(event, context):
    # Procesar cada registro en el evento
    for record in event['Records']:
        s3_bucket = record['s3']['bucket']['name']
        s3_key = record['s3']['object']['key']

        # Llamar a Textract para analizar el documento
        response = textract.analyze_document(
            Document={
                'S3Object': {
                    'Bucket': s3_bucket,
                    'Name': s3_key
                }
            },
            FeatureTypes=['TABLES']
        )

        # Procesar el resultado de Textract y actualizar DynamoDB
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                line_text = item['Text']
                product_id, tenant_id, category, stock = line_text.split(':')
                table = dynamodb.Table(PRODUCTS_TABLE_NAME)
                table.put_item(
                    Item={
                        'ProductId': product_id,
                        'TenantId': tenant_id,
                        'Category': category,
                        'Stock': int(stock)
                    }
                )
    return {
        'statusCode': 200,
        'body': 'Documents processed successfully'
    }
