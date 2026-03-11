class EC2SecurityGroups extends HTMLElement {
    connectedCallback() {
        this._render();
        this._loadSecurityGroups();
    }

    onActivated() {
        this._loadSecurityGroups();
    }

    _render() {
        this.innerHTML = `
            <div class="card">
                <h2>Create Security Group</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>Group Name</label>
                        <input type="text" id="sg-name" placeholder="my-security-group">
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <input type="text" id="sg-desc" placeholder="Description">
                    </div>
                    <button class="btn btn-primary" id="btn-create-sg">Create</button>
                </div>
            </div>

            <div class="card">
                <h2>Security Groups</h2>
                <div id="sg-table"></div>
            </div>

            <div class="card">
                <h2>Ingress Rules</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>Group ID</label>
                        <input type="text" id="ingress-gid" placeholder="sg-...">
                    </div>
                    <div class="form-group">
                        <label>Port</label>
                        <input type="number" id="ingress-port" placeholder="443" value="443">
                    </div>
                    <div class="form-group">
                        <label>CIDR</label>
                        <input type="text" id="ingress-cidr" placeholder="0.0.0.0/0" value="0.0.0.0/0">
                    </div>
                    <button class="btn btn-success" id="btn-authorize">Authorize</button>
                    <button class="btn btn-warning" id="btn-revoke">Revoke</button>
                </div>
            </div>
        `;

        this.querySelector('#btn-create-sg').addEventListener('click', () => this._createSecurityGroup());
        this.querySelector('#btn-authorize').addEventListener('click', () => this._authorizeIngress());
        this.querySelector('#btn-revoke').addEventListener('click',    () => this._revokeIngress());
    }

    async _loadSecurityGroups() {
        try {
            const groups = await adminAPI.listSecurityGroups();
            this._renderTable(groups);
        } catch (e) {
            this.querySelector('#sg-table').innerHTML =
                '<div class="empty-state">Failed to load security groups</div>';
        }
    }

    _renderTable(groups) {
        const container = this.querySelector('#sg-table');
        if (!groups || groups.length === 0) {
            container.innerHTML = '<div class="empty-state">No security groups</div>';
            return;
        }
        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Group ID</th>
                        <th>Name</th>
                        <th>Description</th>
                        <th>VPC</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${groups.map(sg => `
                        <tr>
                            <td>${sg.group_id || ''}</td>
                            <td>${sg.group_name || ''}</td>
                            <td>${sg.description || ''}</td>
                            <td>${sg.vpc_id || ''}</td>
                            <td>
                                <button class="btn btn-sm btn-primary"
                                    onclick="document.querySelector('ec2-security-groups')._useGroupId('${sg.group_id}')">Use</button>
                                <button class="btn btn-sm btn-danger"
                                    onclick="document.querySelector('ec2-security-groups')._deleteSecurityGroup('${sg.group_id}')">Delete</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    _useGroupId(groupId) {
        this.querySelector('#ingress-gid').value = groupId;
    }

    async _createSecurityGroup() {
        const name = this.querySelector('#sg-name').value.trim();
        const desc = this.querySelector('#sg-desc').value.trim();
        if (!name) return alert('Group name is required');
        await adminAPI.createSecurityGroup(name, desc || name);
        this.querySelector('#sg-name').value = '';
        this.querySelector('#sg-desc').value = '';
        this._loadSecurityGroups();
    }

    async _deleteSecurityGroup(groupId) {
        if (!confirm(`Delete security group ${groupId}?`)) return;
        await adminAPI.deleteSecurityGroup(groupId);
        this._loadSecurityGroups();
    }

    async _authorizeIngress() {
        const groupId = this.querySelector('#ingress-gid').value.trim();
        const port    = this.querySelector('#ingress-port').value;
        const cidr    = this.querySelector('#ingress-cidr').value.trim();
        if (!groupId) return alert('Group ID is required');
        if (!port)    return alert('Port is required');
        await adminAPI.authorizeIngress(groupId, port, cidr);
        alert(`Port ${port} authorized for ${groupId}`);
    }

    async _revokeIngress() {
        const groupId = this.querySelector('#ingress-gid').value.trim();
        const port    = this.querySelector('#ingress-port').value;
        const cidr    = this.querySelector('#ingress-cidr').value.trim();
        if (!groupId) return alert('Group ID is required');
        if (!port)    return alert('Port is required');
        await adminAPI.revokeIngress(groupId, port, cidr);
        alert(`Port ${port} revoked for ${groupId}`);
    }
}

customElements.define('ec2-security-groups', EC2SecurityGroups);
