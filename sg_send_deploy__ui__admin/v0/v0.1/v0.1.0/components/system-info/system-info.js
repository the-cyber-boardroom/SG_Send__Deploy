class SystemInfo extends HTMLElement {
    connectedCallback() {
        this._render();
    }

    onActivated() {
        this._loadInfo();
    }

    _render() {
        this.innerHTML = `
            <div class="card">
                <h2>System Information</h2>
                <div class="info-grid" id="system-info-grid">
                    <div class="empty-state">Loading...</div>
                </div>
            </div>
        `;
    }

    async _loadInfo() {
        const grid = this.querySelector('#system-info-grid');
        try {
            const [health, status] = await Promise.all([
                adminAPI.getHealth(),
                adminAPI.getStatus().catch(() => null)
            ]);

            let items = '';

            if (health) {
                items += `
                    <div class="info-item">
                        <label>Health Status</label>
                        <div class="value">${health.status || 'unknown'}</div>
                    </div>
                `;
            }

            if (status) {
                if (status.service_name) {
                    items += `
                        <div class="info-item">
                            <label>Service Name</label>
                            <div class="value">${status.service_name}</div>
                        </div>
                    `;
                }
                if (status.version) {
                    items += `
                        <div class="info-item">
                            <label>Version</label>
                            <div class="value">${status.version}</div>
                        </div>
                    `;
                }
            }

            grid.innerHTML = items || '<div class="empty-state">No system info available</div>';
        } catch (e) {
            grid.innerHTML = '<div class="empty-state">Failed to load system info</div>';
        }
    }
}

customElements.define('system-info', SystemInfo);
