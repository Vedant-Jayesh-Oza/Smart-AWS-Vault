import os
import json
import boto3
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
from flask_cognito import CognitoAuth, cognito_auth_required

load_dotenv()

app = Flask(__name__)
CORS(app)  

app.config['COGNITO_REGION'] = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')  # Change if needed
app.config['COGNITO_USERPOOL_ID'] = os.getenv('COGNITO_USERPOOL_ID')
app.config['COGNITO_APP_CLIENT_ID'] = os.getenv('COGNITO_APP_CLIENT_ID')
app.config['COGNITO_CHECK_TOKEN_EXPIRATION'] = True
app.config['COGNITO_JWT_HEADER_NAME'] = 'Authorization'
app.config['COGNITO_JWT_HEADER_PREFIX'] = 'Bearer'

cognito_auth = CognitoAuth(app)

ec2_client = boto3.client('ec2')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/auth/user', methods=['GET'])
@cognito_auth_required
def get_authenticated_user():
    """Get details of the currently authenticated user"""
    return jsonify({'user': current_user})


@app.route('/api/instances', methods=['GET'])
@cognito_auth_required
def get_instances():
    """Get all EC2 instances and their backup status"""
    try:
        response = ec2_client.describe_instances()

        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                # Check if instance has Backup tag
                backup_enabled = False
                instance_name = instance['InstanceId']

                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                    if tag['Key'] == 'Backup' and tag['Value'].lower() == 'true':
                        backup_enabled = True

                instances.append({
                    'id': instance['InstanceId'],
                    'name': instance_name,
                    'state': instance['State']['Name'],
                    'type': instance['InstanceType'],
                    'backup_enabled': backup_enabled
                })

        return jsonify(instances)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/instances/<instance_id>/toggle-backup', methods=['POST'])
@cognito_auth_required
def toggle_backup(instance_id):
    """Enable or disable backup for an instance by updating its tags"""
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])

        if not response['Reservations']:
            return jsonify({'error': 'Instance not found'}), 404

        instance = response['Reservations'][0]['Instances'][0]

        backup_tag_exists = False
        backup_enabled = False

        for tag in instance.get('Tags', []):
            if tag['Key'] == 'Backup':
                backup_tag_exists = True
                backup_enabled = tag['Value'].lower() == 'true'
                break

        new_backup_state = not backup_enabled

        ec2_client.create_tags(
            Resources=[instance_id],
            Tags=[{'Key': 'Backup', 'Value': str(new_backup_state).lower()}]
        )

        return jsonify({
            'instance_id': instance_id,
            'backup_enabled': new_backup_state
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/snapshots', methods=['GET'])
@cognito_auth_required
def get_snapshots():
    """Get all snapshots created by Smart Vault"""
    try:
        response = ec2_client.describe_snapshots(
            Filters=[
                {
                    'Name': 'tag:CreatedBy',
                    'Values': ['SmartVault']
                }
            ],
            OwnerIds=['self']
        )

        snapshots = []
        for snapshot in response['Snapshots']:
            instance_id = ''
            retention_days = ''
            delete_after = ''

            for tag in snapshot.get('Tags', []):
                if tag['Key'] == 'InstanceId':
                    instance_id = tag['Value']
                elif tag['Key'] == 'RetentionDays':
                    retention_days = tag['Value']
                elif tag['Key'] == 'DeleteAfter':
                    delete_after = tag['Value']

            snapshots.append({
                'id': snapshot['SnapshotId'],
                'volume_id': snapshot['VolumeId'],
                'instance_id': instance_id,
                'state': snapshot['State'],
                'progress': snapshot['Progress'],
                'start_time': snapshot['StartTime'].isoformat(),
                'description': snapshot['Description'],
                'retention_days': retention_days,
                'delete_after': delete_after
            })

        return jsonify(snapshots)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/snapshots/create', methods=['POST'])
@cognito_auth_required
def create_snapshot():
    """Manually create a snapshot for a specific instance"""
    try:
        data = request.json
        instance_id = data.get('instance_id')
        retention_days = int(data.get('retention_days', 7))

        if not instance_id:
            return jsonify({'error': 'Instance ID is required'}), 400

        response = ec2_client.describe_instances(InstanceIds=[instance_id])

        if not response['Reservations']:
            return jsonify({'error': 'Instance not found'}), 404

        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

        snapshots = []

        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                for volume in instance.get('BlockDeviceMappings', []):
                    if 'Ebs' in volume:
                        volume_id = volume['Ebs']['VolumeId']
                        description = f"Manual snapshot of {volume_id} from {instance_id} created at {timestamp}"

                        # Create the snapshot
                        snapshot = ec2_client.create_snapshot(
                            VolumeId=volume_id,
                            Description=description,
                            TagSpecifications=[
                                {
                                    'ResourceType': 'snapshot',
                                    'Tags': [
                                        {'Key': 'Name', 'Value': f"Snapshot-{instance_id}-{volume_id}-{timestamp}"},
                                        {'Key': 'InstanceId', 'Value': instance_id},
                                        {'Key': 'CreatedBy', 'Value': 'SmartVault'},
                                        {'Key': 'RetentionDays', 'Value': str(retention_days)},
                                        {'Key': 'DeleteAfter', 'Value': (datetime.now() + datetime.timedelta(days=retention_days)).strftime('%Y-%m-%d')},
                                        {'Key': 'ManuallyCreated', 'Value': 'true'}
                                    ]
                                }
                            ]
                        )

                        snapshots.append(snapshot['SnapshotId'])

        if not snapshots:
            return jsonify({'message': 'No volumes found to snapshot'}), 404

        return jsonify({
            'message': f"Created {len(snapshots)} snapshots for instance {instance_id}",
            'snapshot_ids': snapshots
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics', methods=['GET'])
@cognito_auth_required
def get_metrics():
    """Get metrics about snapshots and protected instances"""
    try:
        from aws_service import get_metrics
        return jsonify(get_metrics())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
