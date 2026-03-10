class AdminShell extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <div class="header">
                <h1>SG/Send Deploy</h1>
                <div class="nav">
                    <button class="active" data-target="ec2">Infrastructure</button>
                    <button data-target="system">System</button>
                    <button onclick="window.open('/docs','_blank')">Swagger</button>
                </div>
            </div>
            <div class="panel">
                <slot></slot>
            </div>
        `;
        this.querySelectorAll('.nav button[data-target]').forEach(btn => {
            btn.addEventListener('click', () => this._switchPanel(btn));
        });
    }

    _switchPanel(btn) {
        const target = btn.dataset.target;
        this.querySelectorAll('.nav button[data-target]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        this.querySelectorAll('[data-panel]').forEach(panel => {
            if (panel.dataset.panel === target) {
                panel.style.display = '';
                if (panel.onActivated) panel.onActivated();
            } else {
                panel.style.display = 'none';
            }
        });
    }
}

customElements.define('admin-shell', AdminShell);
