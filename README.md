# Smart Vault - Intelligent Backup & Disaster Recovery System

## 📌 Overview
Smart Vault is an automated **EC2 backup and disaster recovery system** that:
- Identifies EC2 instances tagged for backup.
- Creates snapshots of their attached volumes.
- Automatically deletes old snapshots based on retention policy.
- Notifies users of backup events via Amazon SNS.
- Provides a Web UI for managing backups.
- Uses AWS Cognito for secure authentication.

The project is built using **AWS Lambda, EventBridge, SNS, Cognito, Flask (Python API), Docker, and Nginx**.

---
## 🎯 Features
✅ **Automated EC2 Backup & Snapshot Management**  
✅ **Customizable Retention Policy** (Automatically delete old snapshots)  
✅ **Flask API for Managing Backups & Snapshots**  
✅ **Web UI for Managing Backups**  
✅ **AWS EventBridge for Scheduled Execution**  
✅ **Notifications via SNS**  


---
## 🔧 Installation & Setup

### **1️⃣ Prerequisites**
Ensure you have the following installed:
- **Python 3.9+**
- **AWS CLI** (configured with IAM permissions)
- **Docker & Docker Compose**

### **2️⃣ AWS Setup**
The system relies on multiple AWS services:
1. **EC2 Tagging**: Ensure your instances have a `Backup=true` tag.
2. **IAM Role for Lambda**: Attach policies for EC2 & SNS access.
3. **Amazon SNS**: Create an SNS topic for notifications.
4. **EventBridge Rule**: Schedule Lambda execution (e.g., daily backups).
5. **Amazon Cognito**: Secure API authentication.

Refer to the `iam-setup.md`, `eventbridge-setup.md`, and `sns-setup.md` for detailed setup instructions.

### **3️⃣ Running with Docker Compose**
```sh
git clone https://github.com/your-repo/smart-vault.git
cd smart-vault
docker-compose up --build
```
The API will be available at **`http://localhost:5050/api/`**
The frontend will be available at **`http://localhost`**

---
## 🚀 API Endpoints
### **1️⃣ Health Check**
```http
GET /api/health
```
_Check if the API is running._

### **2️⃣ Get EC2 Instances & Backup Status**
```http
GET /api/instances
```
_Returns all EC2 instances and their backup status._

### **3️⃣ Toggle Backup for an Instance**
```http
POST /api/instances/{instance_id}/toggle-backup
```
_Enables/disables backup for a specific EC2 instance._

### **4️⃣ List Snapshots Created by Smart Vault**
```http
GET /api/snapshots
```
_Returns all snapshots created by the system._

### **5️⃣ Manually Create a Snapshot**
```http
POST /api/snapshots/create
{
    "instance_id": "i-xxxxxxxx",
    "retention_days": 7
}
```
_Creates a manual snapshot for a specific instance._

### **6️⃣ Get Backup Metrics**
```http
GET /api/metrics
```
_Returns metrics about snapshots and protected instances._

---
## 🔥 AWS Lambda Function (`snapshot_manager.py`)
- **Identifies instances with `Backup=true` tag**
- **Creates snapshots of attached volumes**
- **Tags snapshots with retention policy**
- **Deletes old snapshots past their retention period**
- **Sends SNS notifications on completion**


## 📝 To-Do & Future Enhancements
- ✅ Implement **Cognito** for User AWS Account Access.
- ✅ Deploy on **AWS Amplify** for user Adoption


