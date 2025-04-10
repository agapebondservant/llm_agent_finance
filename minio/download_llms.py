import os
import boto3
from huggingface_hub import hf_hub_download
from huggingface_hub import snapshot_download

s3_client = boto3.client('s3',
                         aws_access_key_id=os.getenv('MINIO_ACCESS_KEY'),
                         aws_secret_access_key=os.getenv('MINIO_SECRET_KEY'),
                         endpoint_url=f"https://{os.getenv('MINIO_ENDPOINT')}"
                        )

bucket_name = "llm"

def upload_file_to_minio(repo_id, prefix_key, fullfilename=None):
    path = f"./{prefix_key}" if fullfilename is None else fullfilename
    snapshot_download(repo_id=repo_id, cache_dir=path, token=os.getenv('HF_TOKEN'))
    for filename in os.listdir(path):
        fullfilename = path + '/' + filename
        print("Uploading:", fullfilename)
        if os.path.isdir(fullfilename):
            upload_file_to_minio(repo_id, prefix_key, fullfilename)
        else:
            try:
                s3_client.upload_file(fullfilename, bucket_name, prefix_key + '/' + filename)
            except Exception as e:
                print(f"An error occurred while uploading {fullfilename}: {e}")


upload_file_to_minio('meta-llama/Llama-3.1-8B-Instruct', "llama")
upload_file_to_minio('ibm-granite/granite-3.0-8b-instruct', "granite")