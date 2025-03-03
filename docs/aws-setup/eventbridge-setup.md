# EventBridge Schedule Setup for Smart Vault

This document outlines the steps to set up an EventBridge schedule to automatically trigger the Smart Vault Lambda function.

## Create the EventBridge Schedule

1. Sign in to the AWS Management Console and open the Amazon EventBridge console at https://console.aws.amazon.com/events/
2. In the navigation pane, choose **Schedules**.
3. Choose **Create schedule**.

### Basic Details
1. For **Schedule name**, enter `SmartVault-Daily-Backup`.
2. (Optional) Enter a description.
3. For **Schedule pattern**, choose **Recurring schedule**.
4. For **Schedule type**, choose **Rate-based schedule**.
5. Enter `1` for the value and select `Days` for the unit to run the backup daily.
   - Alternatively, you could choose **Cron-based schedule** for more precise timing, such as running at a specific hour.

### Target Details
1. For **Target**, choose **Lambda function**.
2. For **Function**, choose the `SmartVault-SnapshotManager` function you created earlier.
3. Leave all other settings as default.

### Settings
1. For **Timezone**, select your preferred timezone.
2. For **Schedule state**, ensure **Enabled** is selected.
3. Choose **Create schedule**.

## For Hourly Backups (Optional)

If you want to set up an hourly backup schedule for critical systems:

1. Follow the same steps as above, but name the schedule `SmartVault-Hourly-Backup`.
2. For **Schedule type**, choose **Rate-based schedule**.
3. Enter `1` for the value and select `Hours` for the unit.
4. Continue with the target details and settings as described above.

## Testing the Schedule

The schedule will automatically trigger the Lambda function based on the configured schedule. To test immediately:

1. From the **Schedules** page, select the schedule you created.
2. Choose **Actions** and then **Run**.
3. Verify execution in the Lambda function's monitoring tab.