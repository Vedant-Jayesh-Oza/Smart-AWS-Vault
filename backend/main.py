from fastapi import FastAPI, HTTPException
import boto3

app = FastAPI()

ec2 = boto3.client("ec2", region_name="us-east-1")  

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

