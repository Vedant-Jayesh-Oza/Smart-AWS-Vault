# Lambda Function Setup for Smart Vault

This document outlines the steps to set up the Lambda function for Smart Vault in the AWS Console.

## Create the Lambda Function

1. Sign in to the AWS Management Console and open the Lambda console at https://console.aws.amazon.com/lambda/
2. Choose **Create function**.
3. Select **Author from scratch**.
4. For **Function name**, enter `SmartVault-SnapshotManager`.
5. For **Runtime**, select **Python 3.9**.
6. For **Architecture**, choose the default option.
7. Under **Permissions**, expand **Change default execution role**.
8. Select **Use an existing role**.
9. In the **Existing role** dropdown, select `SmartVault-Lambda-Role` (the role you created earlier).
10. Choose **Create function**.

## Configure the Lambda Function

1. In the **Code** tab, replace the default code with the contents of your `snapshot_manager.py` file.
2. Click **Deploy** to save your code.

### Environment Variables

1. Scroll down to the **Environment variables** section.
2. Choose **Edit**.
3. Add the following environment variables:
   - Key: `SNS_TOPIC_ARN`, Value: (leave blank for now, we'll add this after creating the SNS topic)
   - Key: `RETENTION_DAYS`, Value: `7` (or your preferred retention period in days)
4. Choose **Save**.

### General Configuration

1. Scroll to the **General configuration** section and choose **Edit**.
2. Change the **Timeout** to `3 min 0 sec` (snapshots may take some time for multiple instances).
3. (Optional) Adjust the **Memory** to `256 MB` if needed.
4. Choose **Save**.

## Test the Lambda Function

1. Choose the **Test** tab.
2. Choose **Create new event**.
3. For **Event name**, enter `TestEvent`.
4. Leave the default JSON as is (our function doesn't require specific event data).
5. Choose **Save**.
6. Choose **Test** to run the function with the test event.

**Note:** For the function to work correctly, you need to have EC2 instances tagged with `Backup=true`. The test may indicate that no instances were found if you don't have any properly tagged instances.