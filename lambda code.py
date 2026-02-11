import boto3
import os

s3 = boto3.client('s3')
polly = boto3.client('polly')

DESTINATION_BUCKET = os.environ.get('DESTINATION_BUCKET')

def lambda_handler(event, context):

    # Ensure this is an S3 trigger
    if 'Records' not in event:
        print("Lambda invoked without S3 trigger")
        return {"statusCode": 200, "body": "Not an S3 event"}

    try:
        record = event['Records'][0]
        source_bucket = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']

        # ✅ Read text file from S3 (FIXED LINE)
        response = s3.get_object(
            Bucket=source_bucket,
            Key=file_key
        )

        text = response['Body'].read().decode('utf-8')

        # Convert text to speech
        audio = polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId='Joanna'
        )

        audio_key = file_key.replace('.txt', '.mp3')

        # Save audio to destination bucket
        s3.put_object(
            Bucket=DESTINATION_BUCKET,
            Key=audio_key,
            Body=audio['AudioStream'].read(),
            ContentType='audio/mpeg'
        )

        return {
            "statusCode": 200,
            "body": f"Audio file created: {audio_key}"
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": str(e)
        }
