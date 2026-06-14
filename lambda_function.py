import json
import boto3

# Initialize AWS SDK clients
s3 = boto3.client('s3')
sns = boto3.client('sns', region_name='us-east-1')  # Targets your active SNS region

# Configuration constants
BUCKET_NAME = 'event-announcement-project23'
FILE_NAME = 'events.json'
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:707133230145:demo-sns'

def lambda_handler(event, context):
    try:
        # 1. Log the incoming event details for debugging
        print("Received event: " + json.dumps(event))

        # 2. Parse the incoming event details from the frontend directly (handles raw JSON)
        body = json.loads(event) if isinstance(event, str) else event
        
        new_event = {
            "title": body.get('title'),
            "date": body.get('date'),
            "description": body.get('description')
        }

        # 3. Download current events.json from S3
        try:
            s3_response = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME)
            events = json.loads(s3_response['Body'].read().decode('utf-8'))
        except s3.exceptions.NoSuchKey:
            # If the file doesn't exist yet, start with an empty list
            events = []

        # 4. Append the new event to the list
        events.append(new_event)

        # 5. Upload the updated list back to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=FILE_NAME,
            Body=json.dumps(events, indent=2),
            ContentType='application/json'
        )

        # 6. Broadcast notification to all SNS email subscribers
        email_message = f"A new event has been created!\n\nTitle: {new_event['title']}\nDate: {new_event['date']}\nDescription: {new_event['description']}\n\nCheck it out here: http://{BUCKET_NAME}.s3-website-us-west-1.amazonaws.com/"
        
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=email_message,
            Subject=f"New Event Announced: {new_event['title']}"
        )

        # 7. Return successful response to API Gateway
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Enables CORS handles
            },
            'body': json.dumps({'message': 'Event created and notification sent successfully!'})
        }

    except Exception as e:
        # Log any unexpected errors to CloudWatch
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
