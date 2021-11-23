# import json
# import urllib.parse
# import boto3

# print('Loading function')

# s3 = boto3.client('s3')
# translate = boto3.client('translate')
# db_obj = boto3.resource('dynamodb')
# table = db_obj.Table('<table>')


# def lambda_handler(event, context):
#     #print("Received event: " + json.dumps(event, indent=2))

#     # Get the object from the event and show its content type
#     bucket = event['Records'][0]['s3']['bucket']['name']
#     key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
#     try:
#         # S3からオプジェットを取得
#         s3_get_resp = s3.get_object(Bucket=bucket, Key=key)
#         s3_txt = s3_get_resp['Body'].read()
#         s3_txt = s3_txt.decode('utf-8')
#         # 確認
#         #print(s3_txt)
        
#         # 翻訳
#         translate_resp = translate.translate_text(
#             Text=s3_txt,
#             SourceLanguageCode='en',
#             TargetLanguageCode='ja'
#             )
#         translate_txt = translate_resp.get('TranslatedText')
#         # 確認
#         #print(translate_txt)
        
#         # S3にアップロード
#         output_key = 'translated/' + key[7:]
#         #s3_put_resp = s3.put_object(
#         #    Bucket=bucket,
#         #    Key=output_key,
#         #    Body=translate_resp.get('TranslatedText').encode('utf-8')
#         #    )
#         #if s3_put_resp['ResponseMetadata']['HTTPStatusCode'] == 200:
#         #    print('Success')
        
#         # DynamoDBに保存
#         file_date = key[14:-4]
#         db_resp = table.put_item(
#             Item={
#                 'id': int(file_date[0:8]),
#                 'date': int(file_date),
#                 'origin': s3_txt,
#                 'translated': translate_txt,
#                 'speaker': '',
#                 'sid': ''
#             }
#         )
#         if db_resp['ResponseMetadata']['HTTPStatusCode'] == 200:
#             print('Success')
        
            
#         return
#     except Exception as e:
#         print(e)
#         print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
#         raise e
