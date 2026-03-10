class EC2Instances extends HTMLElement {
    connectedCallback() {
        this._refreshInterval = null;
        this._render();
        this.onActivated();
    }

    disconnectedCallback() {
        if (this._refreshInterval) clearInterval(this._refreshInterval);
    }

    onActivated() {
        this._loadInstances();
        if (this._refreshInterval) clearInterval(this._refreshInterval);
        this._refreshInterval = setInterval(() => this._loadInstances(), 30000);
    }

    _render() {
        this.innerHTML = `
            <div class="card">
                <h2>Create Instance</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>Instance Type</label>
                        <select id="create-type">
                            <option value="t3.micro">t3.micro</option>
                            <option value="t3.small">t3.small</option>
                            <option value="t3.medium">t3.medium</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Image ID</label>
                        <input type="text" id="create-ami" placeholder="ami-...">
                    </div>
                    <div class="form-group">
                        <label>Key Name</label>
                        <input type="text" id="create-key" placeholder="key name">
                    </div>
                    <div class="form-group">
                        <label>Data Room ID</label>
                        <input type="text" id="create-room" placeholder="room-...">
                    </div>
                    <button class="btn btn-primary" id="btn-create">Create</button>
                </div>
            </div>

            <div class="card">
                <h2>EC2 Instances</h2>
                <div id="instances-table"></div>
            </div>

            <div class="card" style="display:none" id="audit-card">
                <h2>Audit Log</h2>
                <div id="audit-table"></div>
            </div>

            <button class="btn btn-sm" id="btn-audit" style="margin-top:8px">Toggle Audit Log</button>
        `;

        this.querySelector('#btn-create').addEventListener('click', () => this._createInstance());
        this.querySelector('#btn-audit').addEventListener('click', () => this._toggleAudit());
    }

    async _loadInstances() {
        try {
            const instances = await adminAPI.listInstances();
            this._renderTable(instances);
        } catch (e) {
            this.querySelector('#instances-table').innerHTML =
                '<div class="empty-state">Failed to load instances</div>';
        }
    }

    _renderTable(instances) {
        const container = this.querySelector('#instances-table');
        if (!instances || instances.length === 0) {
            container.innerHTML = '<div class="empty-state">No running instances</div>';
            return;
        }
        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Instance ID</th>
                        <th>Status</th>
                        <th>Type</th>
                        <th>Public IP</th>
                        <th>AMI</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${instances.map(i => `
                        <tr>
                            <td>${i.instance_id || ''}</td>
                            <td><span class="status-badge status-${i.status || ''}">${i.status || ''}</span></td>
                            <td>${i.instance_type || ''}</td>
                            <td>${i.public_ip || ''}</td>
                            <td>${i.ami_id || ''}</td>
                            <td>
                                <button class="btn btn-sm btn-success"  onclick="document.querySelector('ec2-instances')._startInstance('${i.instance_id}')">Start</button>
                                <button class="btn btn-sm btn-warning"  onclick="document.querySelector('ec2-instances')._stopInstance('${i.instance_id}')">Stop</button>
                                <button class="btn btn-sm btn-danger"   onclick="document.querySelector('ec2-instances')._terminateInstance('${i.instance_id}')">Terminate</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    async _createInstance() {
        const type  = this.querySelector('#create-type').value;
        const ami   = this.querySelector('#create-ami').value;
        const key   = this.querySelector('#create-key').value;
        const room  = this.querySelector('#create-room').value;
        await adminAPI.createInstance(type, room, ami, key);
        this._loadInstances();
    }

    async _startInstance(id) {
        await adminAPI.startInstance(id);
        this._loadInstances();
    }

    async _stopInstance(id) {
        await adminAPI.stopInstance(id);
        this._loadInstances();
    }

    async _terminateInstance(id) {
        if (!confirm(`Terminate instance ${id}?`)) return;
        await adminAPI.terminateInstance(id);
        this._loadInstances();
    }

    async _toggleAudit() {
        const card = this.querySelector('#audit-card');
        if (card.style.display === 'none') {
            card.style.display = '';
            const entries = await adminAPI.getAuditLog();
            this._renderAudit(entries);
        } else {
            card.style.display = 'none';
        }
    }

    _renderAudit(entries) {
        const container = this.querySelector('#audit-table');
        if (!entries || entries.length === 0) {
            container.innerHTML = '<div class="empty-state">No audit entries</div>';
            return;
        }
        container.innerHTML = `
            <table>
                <thead>
                    <tr><th>Timestamp</th><th>Action</th><th>Admin</th><th>Details</th><th>Hash</th></tr>
                </thead>
                <tbody>
                    ${entries.map(e => `
                        <tr>
                            <td>${e.timestamp || ''}</td>
                            <td>${e.action || ''}</td>
                            <td>${e.admin || ''}</td>
                            <td><code>${JSON.stringify(e.details || {})}</code></td>
                            <td style="font-family:monospace;font-size:11px">${(e.entry_hash || '').substring(0,12)}...</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
}

customElements.define('ec2-instances', EC2Instances);
