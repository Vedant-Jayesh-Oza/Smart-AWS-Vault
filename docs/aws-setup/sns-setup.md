# SNS Topic Setup for Smart Vault

This document outlines the steps to set up an SNS topic for Smart Vault notifications.

## Create the SNS Topic

1. Sign in to the AWS Management Console and open the Amazon SNS console at https://console.aws.amazon.com/sns/
2. In the navigation pane, choose **Topics**.
3. Choose **Create topic**.

### Topic Details
1. For **Type**, select **Standard**.
2. For **Name**, enter `SmartVault-Notifications`.
3. (Optional) Enter a **Display name** like `SmartVault`.
4. Choose **Create topic**.

## Create a Subscription

1. On the topic details page, choose **Create subscription**.
2. For **Protocol**, choose **Email**.
3. For **Endpoint**, enter the email address where you want to receive notifications.
4. Choose **Create subscription**.
5. Check your email inbox and confirm the subscription by clicking the link in the confirmation email from AWS.

## Update Lambda Function with SNS Topic ARN

1. Copy the **ARN** of the SNS topic you created. It should look like: `arn:aws:sns:region:account-id:SmartVault-Notifications`.
2. Go to the Lambda console at https://console.aws.amazon.com/lambda/
3. Open the `SmartVault-SnapshotManager` function.
4. Scroll down to the **Environment variables** section and choose **Edit**.
5. Update the value of the `SNS_TOPIC_ARN` environment variable with the copied ARN.
6. Choose **Save**.

## Testing SNS Notifications

1. In the SNS console, go to the `SmartVault-Notifications` topic.
2. Choose **Publish message**.
3. For **Subject**, enter `SmartVault - Test Notification`.
4. For **Message**, enter `This is a test notification from Smart Vault.`.
5. Choose **Publish message**.
6. Check your subscribed email address for the test message.