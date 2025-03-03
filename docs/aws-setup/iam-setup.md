# IAM Role Setup for Smart Vault

This document outlines the steps to create an IAM role for the Smart Vault Lambda function.

## Create the IAM Role

1. Sign in to the AWS Management Console and open the IAM console at https://console.aws.amazon.com/iam/
2. In the navigation pane, choose **Roles**, and then choose **Create role**.
3. For **Trusted entity type**, choose **AWS service**.
4. For **Use case**, choose **Lambda**, then choose **Next**.
5. On the **Add permissions** page, search for and select the following policies:
   - `AmazonEC2ReadOnlyAccess`
   - `AmazonSNSFullAccess`
6. Choose **Next**.
7. For **Role name**, enter `SmartVault-Lambda-Role`.
8. (Optional) For **Description**, enter a description for the role.
9. Choose **Create role**.

## Create Custom Policy for EC2 Snapshot Management

1. In the IAM console, choose **Policies**, and then choose **Create policy**.
2. Choose the **JSON** tab and paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateSnapshot",
                "ec2:DeleteSnapshot",
                "ec2:DescribeSnapshots",
                "ec2:CreateTags",
                "ec2:DescribeInstances",
                "ec2:DescribeVolumes"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}