import boto3
import datetime
import os

def get_tagged_instances(ec2_client, tag_key='Backup', tag_value='true'):
    """
    Find all EC2 instances with the specified tag
    """
    print(f"Looking for instances with tag {tag_key}={tag_value}")
    
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': f'tag:{tag_key}',
                'Values': [tag_value]
            }
        ]
    )
    
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'running':
                instances.append(instance['InstanceId'])
                print(f"Found instance: {instance['InstanceId']}")
    
    return instances

def create_snapshot(ec2_client, instance_id, retention_days=7):
    """
    Create a snapshot of all volumes attached to the instance
    """
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    
    snapshots = []
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            for volume in instance.get('BlockDeviceMappings', []):
                if 'Ebs' in volume:
                    volume_id = volume['Ebs']['VolumeId']
                    description = f"Snapshot of {volume_id} from {instance_id} created at {timestamp}"
                    
                    print(f"Creating snapshot of volume {volume_id} from instance {instance_id}")
                    
                    snapshot = ec2_client.create_snapshot(
                        VolumeId=volume_id,
                        Description=description,
                        TagSpecifications=[
                            {
                                'ResourceType': 'snapshot',
                                'Tags': [
                                    {
                                        'Key': 'Name',
                                        'Value': f"Snapshot-{instance_id}-{volume_id}-{timestamp}"
                                    },
                                    {
                                        'Key': 'InstanceId',
                                        'Value': instance_id
                                    },
                                    {
                                        'Key': 'CreatedBy',
                                        'Value': 'SmartVault'
                                    },
                                    {
                                        'Key': 'RetentionDays',
                                        'Value': str(retention_days)
                                    },
                                    {
                                        'Key': 'DeleteAfter',
                                        'Value': (datetime.datetime.now() + datetime.timedelta(days=retention_days)).strftime('%Y-%m-%d')
                                    }
                                ]
                            }
                        ]
                    )
                    
                    snapshots.append(snapshot['SnapshotId'])
                    print(f"Created snapshot: {snapshot['SnapshotId']}")
    
    return snapshots

def delete_old_snapshots(ec2_client):
    """
    Delete snapshots that have passed their retention period
    """
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    print(f"Looking for snapshots to delete (DeleteAfter <= {today})")
    
    response = ec2_client.describe_snapshots(
        Filters=[
            {
                'Name': 'tag:CreatedBy',
                'Values': ['SmartVault']
            }
        ],
        OwnerIds=['self']
    )
    
    for snapshot in response['Snapshots']:
        delete_after = None
        
        for tag in snapshot.get('Tags', []):
            if tag['Key'] == 'DeleteAfter':
                delete_after = tag['Value']
                break
        
        # If the snapshot is past its retention date, delete it
        if delete_after and delete_after <= today:
            snapshot_id = snapshot['SnapshotId']
            print(f"Deleting snapshot {snapshot_id} (DeleteAfter={delete_after})")
            
            try:
                ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted snapshot: {snapshot_id}")
            except Exception as e:
                print(f"Error deleting snapshot {snapshot_id}: {str(e)}")

def send_notification(sns_client, topic_arn, subject, message):
    """
    Send SNS notification
    """
    try:
        sns_client.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        print(f"Notification sent to {topic_arn}")
    except Exception as e:
        print(f"Error sending notification: {str(e)}")

def lambda_handler(event, context):
    """
    Main Lambda function handler
    """
    print("Starting Smart Vault backup process")
    
    # Initialize AWS clients
    ec2_client = boto3.client('ec2')
    sns_client = boto3.client('sns')
    
    sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
    
    retention_days = int(os.environ.get('RETENTION_DAYS', '7'))
    
    try:
        # 1. Find all instances with the Backup tag
        instances = get_tagged_instances(ec2_client)
        
        if not instances:
            message = "No instances found with Backup=true tag"
            print(message)
            if sns_topic_arn:
                send_notification(sns_client, sns_topic_arn, "Smart Vault - No Instances Found", message)
            return {
                'statusCode': 200,
                'body': message
            }
            
        # 2. Create snapshots for each instance
        snapshot_count = 0
        for instance_id in instances:
            snapshots = create_snapshot(ec2_client, instance_id, retention_days)
            snapshot_count += len(snapshots)
        
        # 3. Delete old snapshots
        delete_old_snapshots(ec2_client)
        
        message = f"Successfully created {snapshot_count} snapshots for {len(instances)} instances"
        print(message)
        if sns_topic_arn:
            send_notification(sns_client, sns_topic_arn, "Smart Vault - Backup Successful", message)
        
        return {
            'statusCode': 200,
            'body': message
        }
    
    except Exception as e:
        error_message = f"Error in Smart Vault backup process: {str(e)}"
        print(error_message)
        
        if sns_topic_arn:
            send_notification(sns_client, sns_topic_arn, "Smart Vault - Backup Failed", error_message)
        
        return {
            'statusCode': 500,
            'body': error_message
        }