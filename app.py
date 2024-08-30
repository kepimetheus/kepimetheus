# app.py
import os
import logging
import re
from flask import Flask, render_template, request, jsonify, send_from_directory
import boto3
import json
from dotenv import load_dotenv
from botocore.exceptions import ClientError, EndpointConnectionError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists (for local development)
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__, static_folder='static')

# Serve static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Initialize Bedrock clients
try:
    bedrock = boto3.client(
        service_name='bedrock',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    # Test the connection and list available models
    response = bedrock.list_foundation_models()
    logger.info("Successfully connected to Amazon Bedrock")
    logger.info("Available models:")
    for model in response['modelSummaries']:
        logger.info(f"Model ID: {model['modelId']}, Name: {model['modelName']}")
except ClientError as e:
    logger.error(f"Error initializing Bedrock client: {e}")
    bedrock = None
    bedrock_runtime = None
except EndpointConnectionError as e:
    logger.error(f"Error connecting to Bedrock endpoint: {e}")
    bedrock = None
    bedrock_runtime = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/transform', methods=['POST'])
def transform():
    if not bedrock_runtime:
        logger.error('Bedrock client not initialized')
        return jsonify({'error': 'Bedrock client not initialized. Check your AWS credentials and region.'}), 500

    natural_language = request.json['query']
    logger.info(f"Received query: {natural_language}")
    
    # Prepare the prompt for Bedrock
    prompt = f"Human: Convert the following natural language query to PromQL (Prometheus Query Language). Only provide the PromQL command without any explanation:\n\n{natural_language}\n\nAssistant: Here's the PromQL command:\n\n"

    try:
        # Call Bedrock Runtime API
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-v2",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 500,
                "temperature": 0.5,
                "top_p": 1,
                "top_k": 250,
                "stop_sequences": ["\n\nHuman:"]
            })
        )

        # Parse the response
        response_body = json.loads(response['body'].read())
        full_response = response_body['completion'].strip()
        
        # Extract only the PromQL query
        promql = re.search(r'`(.*?)`', full_response, re.DOTALL)
        if promql:
            promql = promql.group(1).strip()
        else:
            promql = full_response.split('\n')[0].strip()  # Fallback to first line if no backticks

        logger.info(f"Generated PromQL: {promql}")

        return jsonify({'promql': promql})
    except ClientError as e:
        logger.error(f"Error calling Bedrock API: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')