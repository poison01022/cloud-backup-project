from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import boto3
import os
from werkzeug.utils import secure_filename
from io import BytesIO

# (Optional) Load environment variables if you're using a .env file
#from dotenv import load_dotenv
#load_dotenv()

# Create the Flask app instance
app = Flask(__name__)
CORS(app)  # Enable CORS for your frontend

# Define a root route to confirm the backend is running
@app.route('/')
def index():
    return "Backend is running. Use /upload, /files, or /download/<filename>."

# AWS S3 configuration
S3_BUCKET = 'my-cloud-backup-bucket'  # Replace with your bucket name
S3_REGION = 'ap-northeast-1'  # Replace with your bucket’s region

# Initialize boto3 S3 client using credentials from environment variables
s3 = boto3.client('s3',
                  region_name=S3_REGION,
                  aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                  aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    try:
        s3.upload_fileobj(file, S3_BUCKET, filename)
        return jsonify({'message': f'{filename} uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/files', methods=['GET'])
def list_files():
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET)
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append(obj['Key'])
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        file_obj = BytesIO()
        s3.download_fileobj(S3_BUCKET, filename, file_obj)
        file_obj.seek(0)
        return send_file(file_obj, download_name=filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
