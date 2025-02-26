from fastapi import FastAPI, HTTPException
import boto3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve AWS credentials from environment variables
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

# Initialize AWS EC2 client using credentials from environment variables
ec2 = boto3.client(
    "ec2",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Smart Vault API is running!"}

@app.get("/instances")
def get_instances():
    try:
        response = ec2.describe_instances(
            Filters=[{"Name": "tag:Backup", "Values": ["True"]}]
        )

        instances = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instances.append({
                    "InstanceId": instance["InstanceId"],
                    "State": instance["State"]["Name"],
                    "Tags": instance.get("Tags", []),
                })

        return {"instances": instances}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backup/{instance_id}")
def trigger_backup(instance_id: str):
    try:
        volumes = ec2.describe_volumes(
            Filters=[{"Name": "attachment.instance-id", "Values": [instance_id]}]
        )["Volumes"]

        snapshot_ids = []
        for volume in volumes:
            snapshot = ec2.create_snapshot(
                VolumeId=volume["VolumeId"],
                Description=f"Smart Vault Backup - Instance {instance_id}"
            )
            snapshot_ids.append(snapshot["SnapshotId"])

        return {"message": "Backup started", "snapshots": snapshot_ids}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
