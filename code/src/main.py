from google.cloud import storage
import subprocess
import os



def process_new_file(event, context):
    """Triggered by a new file in Cloud Storage and processes the file."""
    bucket_name = event['bucket']
    file_name = event['name']
    gcs_path = f"gs://{bucket_name}/{file_name}"
    
    print(f"New file detected: {gcs_path}")

    # Local temp file path
    local_path = f"/tmp/{file_name}"

    # Download file from GCS to /tmp/
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(local_path)

    print(f"File downloaded to {local_path}")

    # Run your script with the local file path
    try:
        subprocess.run(["python3", "classify_email.py", local_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running classify_email.py: {e}")

    print("Processing complete.")

