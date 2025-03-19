import { Auth } from 'aws-amplify';


class SmartVaultAPI {
    constructor(baseUrl = window.location.hostname === 'localhost' ? 'http://localhost:5050' : '/api') {
        this.baseUrl = baseUrl;
    }

    async getAuthToken() {
        try {
            const user = await Auth.currentAuthenticatedUser();
            return user.signInUserSession.idToken.jwtToken;
        } catch (error) {
            console.error("User is not authenticated:", error);
            throw new Error("User is not authenticated");
        }
    }

    
    async request(endpoint, options = {}) {
        try {
            const url = `${this.baseUrl}${endpoint}`;
            const token = await this.getAuthToken();

            if (!options.headers) {
                options.headers = {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                };
            } else {
                options.headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(url, options);

            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed: ${error.message}`);
            throw error;
        }
    }


    async getInstances() {
        return this.request('/api/instances');
    }


    async toggleBackup(instanceId) {
        return this.request(`/api/instances/${instanceId}/toggle-backup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
    }

    
    async getSnapshots() {
        return this.request('/api/snapshots');
    }

    
    async createSnapshot(instanceId, retentionDays) {
        return this.request('/api/snapshots/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instance_id: instanceId, retention_days: retentionDays })
        });
    }

    
    async getMetrics() {
        return this.request('/api/metrics');
    }


    async getAuthenticatedUser() {
        return this.request('/api/auth/user');
    }
}

const api = new SmartVaultAPI();

export default api;
