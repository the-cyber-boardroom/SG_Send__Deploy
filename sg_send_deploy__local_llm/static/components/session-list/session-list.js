// ═══════════════════════════════════════════════════════════════════════════════
// Session List — sidebar with saved conversations
// ═══════════════════════════════════════════════════════════════════════════════

class SessionList extends HTMLElement {
    connectedCallback() {
        this.sessions      = []
        this.activeSession = null
        this.render()
        this.loadSessions()

        document.addEventListener('session-saved', () => this.loadSessions())
    }

    render() {
        this.innerHTML = `
            <div class="session-list">
                <div class="session-list-header">
                    <h3>Sessions</h3>
                    <button class="btn-new-chat" id="btn-new-chat">+ New</button>
                </div>
                <div class="session-items" id="session-items"></div>
            </div>`

        this.querySelector('#btn-new-chat').addEventListener('click', () => {
            this.activeSession = null
            this.renderItems()
            const chatPanel = document.querySelector('chat-panel')
            if (chatPanel) chatPanel.newChat()
        })
    }

    async loadSessions() {
        try {
            this.sessions = await llmAPI.listSessions()
            this.renderItems()
        } catch (e) {
            console.warn('Could not load sessions:', e)
        }
    }

    renderItems() {
        const container = this.querySelector('#session-items')
        if (!container) return

        container.innerHTML = this.sessions.map(s => `
            <div class="session-item ${s.id === this.activeSession ? 'active' : ''}" data-id="${s.id}">
                <span class="delete-btn" data-delete="${s.id}">×</span>
                <div class="title">${this.escapeHtml(s.title || 'Untitled')}</div>
                <div class="meta">${s.model} · ${s.message_count} msgs</div>
            </div>
        `).join('')

        container.querySelectorAll('.session-item').forEach(el => {
            el.addEventListener('click', (e) => {
                if (e.target.dataset.delete) return
                this.selectSession(el.dataset.id)
            })
        })

        container.querySelectorAll('.delete-btn').forEach(el => {
            el.addEventListener('click', (e) => {
                e.stopPropagation()
                this.deleteSession(el.dataset.delete)
            })
        })
    }

    async selectSession(id) {
        this.activeSession = id
        this.renderItems()
        try {
            const session   = await llmAPI.getSession(id)
            const chatPanel = document.querySelector('chat-panel')
            if (chatPanel) chatPanel.loadSession(session)
        } catch (e) {
            console.warn('Could not load session:', e)
        }
    }

    async deleteSession(id) {
        try {
            await llmAPI.deleteSession(id)
            this.sessions = this.sessions.filter(s => s.id !== id)
            if (this.activeSession === id) {
                this.activeSession = null
                const chatPanel = document.querySelector('chat-panel')
                if (chatPanel) chatPanel.newChat()
            }
            this.renderItems()
        } catch (e) {
            console.warn('Could not delete session:', e)
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div')
        div.textContent = text
        return div.innerHTML
    }
}

customElements.define('session-list', SessionList)
