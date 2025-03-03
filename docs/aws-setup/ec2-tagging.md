# EC2 Instance Tagging for Smart Vault

This document outlines the steps to tag EC2 instances for inclusion in the Smart Vault backup process.

## Tagging an Existing EC2 Instance

1. Sign in to the AWS Management Console and open the Amazon EC2 console at https://console.aws.amazon.com/ec2/
2. In the navigation pane, choose **Instances**.
3. Select the instance you want to include in the backup process.
4. Choose **Actions**, then **Instance settings**, then **Manage tags**.
5. Choose **Add tag**.
6. For **Key**, enter `Backup`.
7. For **Value**, enter `true`.
8. Choose **Save**.

## Tagging Multiple Instances

To tag multiple instances at once:

1. In the EC2 console, select all the instances you want to tag.
2. Choose **Actions**, then **Instance settings**, then **Manage tags**.
3. Choose **Add tag**.
4. Enter the tag details as described above.
5. Choose **Save**.

## Verifying Tags

To verify that your instances are properly tagged:

1. In the EC2 console, you can filter instances by tag:
2. In the search bar above the instance list, enter `tag:Backup=true`.
3. The results should show only the instances you've tagged for backup.

## Testing the Backup Process

After tagging your instances:

1. Go to the Lambda console and open the `SmartVault-SnapshotManager` function.
2. Choose the **Test** tab and run your test event.
3. The function should now find your tagged instances and create snapshots.
4. You can verify this by checking the CloudWatch logs for the function.
5. You can also check the EC2 console under **Snapshots** to see the newly created snapshots.