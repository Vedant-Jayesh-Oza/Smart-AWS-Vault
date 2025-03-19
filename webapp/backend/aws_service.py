import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def get_metrics():
    """
    Get basic metrics about our EC2 snapshots
    """
    ec2_client = boto3.client('ec2')
    
    response = ec2_client.describe_snapshots(
        Filters=[
            {
                'Name': 'tag:CreatedBy',
                'Values': ['SmartVault']
            }
        ],
        OwnerIds=['self']
    )
    
    total_snapshots = len(response['Snapshots'])
    total_size_gb = sum(snapshot['VolumeSize'] for snapshot in response['Snapshots']) if total_snapshots > 0 else 0
    
    snapshots_by_state = {}
    for snapshot in response['Snapshots']:
        state = snapshot['State']
        if state in snapshots_by_state:
            snapshots_by_state[state] += 1
        else:
            snapshots_by_state[state] = 1
    
    instance_response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Backup',
                'Values': ['true']
            }
        ]
    )
    
    protected_instances = 0
    for reservation in instance_response['Reservations']:
        protected_instances += len(reservation['Instances'])
    
    return {
        'total_snapshots': total_snapshots,
        'total_size_gb': total_size_gb,
        'snapshots_by_state': snapshots_by_state,
        'protected_instances': protected_instances
    }