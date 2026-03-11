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

    // Key Pairs
    async listKeyPairs() {
        return this._fetch('/ec2-key-pairs/key-pairs');
    }

    async createKeyPair(keyName) {
        const params = new URLSearchParams({ key_name: keyName });
        return this._fetch(`/ec2-key-pairs/create-key-pair?${params}`, { method: 'POST' });
    }

    async deleteKeyPair(keyPairId) {
        return this._fetch(`/ec2-key-pairs/delete/${keyPairId}`, { method: 'DELETE' });
    }

    // Security Groups
    async listSecurityGroups() {
        return this._fetch('/ec2-security-groups/security-groups');
    }

    async createSecurityGroup(groupName, description) {
        const params = new URLSearchParams({ group_name: groupName, description: description || '' });
        return this._fetch(`/ec2-security-groups/create-security-group?${params}`, { method: 'POST' });
    }

    async deleteSecurityGroup(groupId) {
        return this._fetch(`/ec2-security-groups/delete/${groupId}`, { method: 'DELETE' });
    }

    async authorizeIngress(groupId, port, cidrIp) {
        const params = new URLSearchParams({ group_id: groupId, port: String(port), cidr_ip: cidrIp || '0.0.0.0/0' });
        return this._fetch(`/ec2-security-groups/authorize-ingress?${params}`, { method: 'POST' });
    }

    async revokeIngress(groupId, port, cidrIp) {
        const params = new URLSearchParams({ group_id: groupId, port: String(port), cidr_ip: cidrIp || '0.0.0.0/0' });
        return this._fetch(`/ec2-security-groups/revoke-ingress?${params}`, { method: 'POST' });
    }

    async getHealth() {
        return this._fetch('/info/health');
    }

    async getStatus() {
        return this._fetch('/info/status');
    }
}

const adminAPI = new AdminAPI();
