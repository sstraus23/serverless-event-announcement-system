# Serverless Event Announcement System

## Overview
A live serverless web application where users submit event announcements through a static frontend, triggering a Lambda function that updates an S3 data store and broadcasts real-time email alerts to verified subscribers via Amazon SNS.

## Architecture
Frontend (S3 Static Site) → API Gateway → AWS Lambda (Python/Boto3) → S3 (Data Store) + Amazon SNS (Email Notifications)

## AWS Services Used
- Amazon S3 — Static website hosting and JSON data storage
- AWS Lambda (Python/Boto3) — Backend logic and event processing
- Amazon API Gateway — RESTful endpoint connecting frontend to Lambda
- Amazon SNS — Real-time email broadcast to verified subscribers

## Key Skills Demonstrated
- Decoupled serverless architecture
- RESTful API design and integration
- Event-driven notification systems
- Cross-region AWS service configuration
- CloudWatch log analysis and production debugging

## Challenges & Solutions

### Challenge 1 — Cross-Region SNS Silent Failure
**The Problem:** The core website and Lambda infrastructure were built in us-west-1 but the SNS topic lived in us-east-1. The default Boto3 configuration caused email alerts to drop silently without any error message.

**The Investigation:** Traced the silent failure through CloudWatch logs and identified that the Boto3 client was initializing locally without targeting the correct regional endpoint.

**The Solution:** Explicitly directed traffic to the correct region in the client initializer:
```python
sns = boto3.client('sns', region_name='us-east-1')
```

### Challenge 2 — API Gateway Payload Mismatch
**The Problem:** The frontend form showed a success popup but no email was sent and no data was written to S3. Because the frontend handled errors silently there was no immediate indication of what failed.

**The Investigation:** Navigated to CloudWatch Logs and inspected the real-time execution streams, discovering a persistent KeyError crash at the body ingestion line. API Gateway was forwarding unmapped raw JSON streams directly instead of the expected proxy wrapper structure.

**The Solution:** Simplified the Python runtime parsing logic to handle conditional serialization directly:
```python
body = json.loads(event) if isinstance(event, str) else event
```

### Challenge 3 — S3 Static Website Routing
**The Problem:** After uploading updated code, the live site continued running stale cached code throwing false positive notifications.

**The Solution:** Identified a browser caching issue and performed a hard refresh, then standardized all deployment filenames to exactly `index.html` to match S3 static website hosting requirements.

## How to Deploy
1. Create an S3 bucket for static website hosting
2. Create a second S3 bucket for JSON data storage
3. Deploy the Lambda function with Python runtime
4. Configure API Gateway with a POST endpoint pointing to Lambda
5. Create an SNS topic and add verified subscriber email addresses
6. Update the frontend with your API Gateway endpoint URL
7. Upload frontend files to the S3 static hosting bucket
