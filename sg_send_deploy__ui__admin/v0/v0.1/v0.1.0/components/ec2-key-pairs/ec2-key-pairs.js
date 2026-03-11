class EC2KeyPairs extends HTMLElement {
    connectedCallback() {
        this._render();
        this._loadKeyPairs();
    }

    onActivated() {
        this._loadKeyPairs();
    }

    _render() {
        this.innerHTML = `
            <div class="card">
                <h2>Create Key Pair</h2>
                <div class="form-row">
                    <div class="form-group">
                        <label>Key Name</label>
                        <input type="text" id="kp-name" placeholder="my-key-pair">
                    </div>
                    <button class="btn btn-primary" id="btn-create-kp">Create</button>
                </div>
            </div>

            <div class="card">
                <h2>Key Pairs</h2>
                <div id="kp-table"></div>
            </div>
        `;

        this.querySelector('#btn-create-kp').addEventListener('click', () => this._createKeyPair());
    }

    async _loadKeyPairs() {
        try {
            const keyPairs = await adminAPI.listKeyPairs();
            this._renderTable(keyPairs);
        } catch (e) {
            this.querySelector('#kp-table').innerHTML =
                '<div class="empty-state">Failed to load key pairs</div>';
        }
    }

    _renderTable(keyPairs) {
        const container = this.querySelector('#kp-table');
        if (!keyPairs || keyPairs.length === 0) {
            container.innerHTML = '<div class="empty-state">No key pairs</div>';
            return;
        }
        container.innerHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Key Pair ID</th>
                        <th>Key Name</th>
                        <th>Key Type</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${keyPairs.map(kp => `
                        <tr>
                            <td>${kp.key_pair_id || ''}</td>
                            <td>${kp.key_name || ''}</td>
                            <td>${kp.key_type || ''}</td>
                            <td>${kp.created || ''}</td>
                            <td>
                                <button class="btn btn-sm btn-danger"
                                    onclick="document.querySelector('ec2-key-pairs')._deleteKeyPair('${kp.key_pair_id}')">Delete</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    async _createKeyPair() {
        const name = this.querySelector('#kp-name').value.trim();
        if (!name) return alert('Key name is required');
        await adminAPI.createKeyPair(name);
        this.querySelector('#kp-name').value = '';
        this._loadKeyPairs();
    }

    async _deleteKeyPair(keyPairId) {
        if (!confirm(`Delete key pair ${keyPairId}?`)) return;
        await adminAPI.deleteKeyPair(keyPairId);
        this._loadKeyPairs();
    }
}

customElements.define('ec2-key-pairs', EC2KeyPairs);
