# app.py
import os
import logging
import re
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import boto3
import json
from dotenv import load_dotenv
from botocore.exceptions import ClientError, EndpointConnectionError
from promql_parser import parse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists (for local development)
if os.path.exists('.env'):
    load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# Serve static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Initialize Bedrock client
try:
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    logger.info("Successfully connected to Amazon Bedrock")
except ClientError as e:
    logger.error(f"Error initializing Bedrock client: {e}")
    bedrock = None
except EndpointConnectionError as e:
    logger.error(f"Error connecting to Bedrock endpoint: {e}")
    bedrock = None

def is_valid_promql(query):
    try:
        parse(query)
        return True
    except Exception as e:
        logger.error(f"Invalid PromQL: {e}")
        return False

def generate_promql(natural_language):
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-v2",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": f"\nHuman: Convert the following natural language query to PromQL (Prometheus Query Language). Only provide the PromQL command without any explanation:\n\n{natural_language}\n\nAssistant: Here's the PromQL command:\n\n",
                "max_tokens_to_sample": 500,
                "temperature": 0.5,
                "top_p": 1,
                "top_k": 250,
                "stop_sequences": ["\n\nHuman:"]
            })
        )

        response_body = json.loads(response['body'].read())
        full_response = response_body['completion']
        
        promql = re.search(r'`(.*?)`', full_response, re.DOTALL)
        if promql:
            promql = promql.group(1).strip()
        else:
            items = full_response.split('\n')
            for item in items:
                if item is not None and item != "":
                    promql = item.strip()
                    break

        return promql
    except Exception as e:
        logger.error(f"Error generating PromQL: {e}")
        return None

def validate_and_correct_promql(promql, natural_language):
    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-v2",
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "prompt": f"\nHuman: The following PromQL query was generated from this natural language query: '{natural_language}'\n\nGenerated PromQL: {promql}\n\nIs this PromQL query valid? If not, please provide a corrected, valid PromQL query that matches the intent of the natural language query. Only provide the corrected PromQL command without any explanation.\n\nAssistant: Here's the corrected PromQL command:\n\n",
                "max_tokens_to_sample": 500,
                "temperature": 0.5,
                "top_p": 1,
                "top_k": 250,
                "stop_sequences": ["\n\nHuman:"]
            })
        )

        response_body = json.loads(response['body'].read())
        full_response = response_body['completion']
        
        corrected_promql = re.search(r'`(.*?)`', full_response, re.DOTALL)
        if corrected_promql:
            corrected_promql = corrected_promql.group(1).strip()
        else:
            items = full_response.split('\n')
            for item in items:
                if item is not None and item != "":
                    corrected_promql = item.strip()
                    break

        return corrected_promql
    except Exception as e:
        logger.error(f"Error validating and correcting PromQL: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/transform', methods=['POST'])
def transform():
    if not bedrock:
        logger.error('Bedrock client not initialized')
        return jsonify({'error': 'Bedrock client not initialized. Check your AWS credentials and region.'}), 500

    natural_language = request.json['question']
    logger.info(f"Received question: {natural_language}")
    
    try:
        # First attempt to generate PromQL
        promql = generate_promql(natural_language)
        if not promql:
            return jsonify({'error': 'Failed to generate PromQL'}), 500

        logger.info(f"Initially generated PromQL: {promql}")

        # Validate the PromQL
        if not is_valid_promql(promql):
            logger.info("Initial PromQL is not valid. Attempting to correct...")
            promql = validate_and_correct_promql(promql, natural_language)
            if not promql:
                return jsonify({'error': 'Failed to generate valid PromQL'}), 500
            
            logger.info(f"Corrected PromQL: {promql}")

            # Validate the corrected PromQL
            if not is_valid_promql(promql):
                return jsonify({'error': 'Generated PromQL is not valid even after correction'}), 400

        return jsonify({'promql': promql})
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
