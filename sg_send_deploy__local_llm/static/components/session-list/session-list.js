// ═══════════════════════════════════════════════════════════════════════════════
// Session List — sidebar with saved conversations, opens chats as sg-layout tabs
// ═══════════════════════════════════════════════════════════════════════════════

class SessionList extends HTMLElement {
    connectedCallback() {
        this.sessions      = []
        this.activeSession = null
        this.render()
        this.loadSessions()

        document.addEventListener('session-saved', () => this.loadSessions())
    }

    get layout() {
        return document.getElementById('main-layout')
    }

    get chatStackId() {
        return window.__chatStackId
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
            this.openNewChatTab()
        })
    }

    openNewChatTab() {
        const layout  = this.layout
        const stackId = this.chatStackId
        if (!layout || !stackId) return

        layout.addTabToStack(stackId, {
            tag   : 'chat-panel',
            title : 'New Chat'
        }, true)
    }

    openSessionInTab(session) {
        const layout  = this.layout
        const stackId = this.chatStackId
        if (!layout || !stackId) return

        // Check if this session is already open in a tab
        const tree      = layout.getLayout()
        const chatStack = this._findStack(tree, stackId)
        if (chatStack) {
            for (let i = 0; i < chatStack.tabs.length; i++) {
                const tab = chatStack.tabs[i]
                if (tab.state && tab.state.sessionId === session.id) {
                    // Tab already open — switch to it
                    layout._switchTab(
                        layout._findNodeById(layout._tree, stackId),
                        i
                    )
                    layout._renderTree()
                    layout._mountAllTabs()
                    return
                }
            }
        }

        // Create a new tab with the session data passed via state
        const tabId = layout.addTabToStack(stackId, {
            tag   : 'chat-panel',
            title : session.title || 'Chat',
            state : { sessionId: session.id }
        }, true)
    }

    _findStack(node, id) {
        if (!node) return null
        if (node.id === id) return node
        if (node.children) {
            for (const child of node.children) {
                const found = this._findStack(child, id)
                if (found) return found
            }
        }
        if (node.tabs) {
            for (const tab of node.tabs) {
                const found = this._findStack(tab, id)
                if (found) return found
            }
        }
        return null
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
                <span class="delete-btn" data-delete="${s.id}">&times;</span>
                <div class="title">${this.escapeHtml(s.title || 'Untitled')}</div>
                <div class="meta">${s.model} &middot; ${s.message_count} msgs</div>
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
            const session = await llmAPI.getSession(id)
            this.openSessionInTab(session)
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
