class AdminAPI {
    constructor() {
        this.baseUrl = '';
    }

    async _fetch(path, options = {}) {
        const response = await fetch(`${this.baseUrl}${path}`, {
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        return response.json();
    }

    async listInstances() {
        return this._fetch('/ec2/instances');
    }

    async getInstance(instanceId) {
        return this._fetch(`/ec2/instances/${instanceId}`);
    }

    async createInstance(instanceType, dataRoomId, imageId, keyName) {
        const params = new URLSearchParams({
            instance_type: instanceType,
            data_room_id:  dataRoomId || '',
            image_id:      imageId    || '',
            key_name:      keyName    || ''
        });
        return this._fetch(`/ec2/create-instance?${params}`, { method: 'POST' });
    }

    async terminateInstance(instanceId) {
        return this._fetch(`/ec2/terminate/${instanceId}`, { method: 'DELETE' });
    }

    async startInstance(instanceId) {
        return this._fetch(`/ec2/start/${instanceId}`, { method: 'POST' });
    }

    async stopInstance(instanceId) {
        return this._fetch(`/ec2/stop/${instanceId}`, { method: 'POST' });
    }

    async getAuditLog() {
        return this._fetch('/ec2/audit-log');
    }

    async getHealth() {
        return this._fetch('/info/health');
    }

    async getStatus() {
        return this._fetch('/info/status');
    }
}

const adminAPI = new AdminAPI();
