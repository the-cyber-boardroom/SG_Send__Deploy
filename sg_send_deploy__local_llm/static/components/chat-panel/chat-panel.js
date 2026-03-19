// ═══════════════════════════════════════════════════════════════════════════════
// Chat Panel — main chat interface with streaming responses
// ═══════════════════════════════════════════════════════════════════════════════

class ChatPanel extends HTMLElement {
    connectedCallback() {
        this.currentModel    = 'gemma3:4b'
        this.messages        = []
        this.currentSessionId = null
        this.isStreaming      = false
        this.render()
        this.loadModels()
    }

    render() {
        this.innerHTML = `
            <div class="chat-panel">
                <div class="chat-header">
                    <select id="model-picker"></select>
                    <span id="chat-status" style="font-size:12px;color:var(--color-text-muted)"></span>
                </div>
                <div class="chat-messages" id="chat-messages"></div>
                <div class="chat-input-area">
                    <textarea id="chat-input" placeholder="Type a message..." rows="1"></textarea>
                    <button class="btn-send" id="btn-send">Send</button>
                </div>
            </div>`

        this.querySelector('#btn-send').addEventListener('click', () => this.sendMessage())
        this.querySelector('#chat-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                this.sendMessage()
            }
        })
        this.querySelector('#model-picker').addEventListener('change', (e) => {
            this.currentModel = e.target.value
        })
    }

    async loadModels() {
        try {
            const models = await llmAPI.listModels()
            const picker = this.querySelector('#model-picker')
            picker.innerHTML = models.map(m =>
                `<option value="${m.name}" ${m.name === this.currentModel ? 'selected' : ''}>${m.name}</option>`
            ).join('')
            if (models.length > 0 && !models.find(m => m.name === this.currentModel)) {
                this.currentModel = models[0].name
            }
        } catch (e) {
            console.warn('Could not load models:', e)
        }
    }

    async sendMessage() {
        const input   = this.querySelector('#chat-input')
        const content = input.value.trim()
        if (!content || this.isStreaming) return

        input.value     = ''
        this.isStreaming = true
        this.querySelector('#btn-send').disabled = true

        this.messages.push({ role: 'user', content })
        this.renderMessages()

        this.messages.push({ role: 'assistant', content: '' })
        this.renderMessages()

        try {
            const response = await llmAPI.chatStream(this.currentModel, this.messages.slice(0, -1))
            const reader   = response.body.getReader()
            const decoder  = new TextDecoder()
            let   buffer   = ''

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                buffer += decoder.decode(value, { stream: true })
                const lines = buffer.split('\n')
                buffer = lines.pop()

                for (const line of lines) {
                    if (!line.trim()) continue
                    try {
                        const chunk = JSON.parse(line)
                        if (chunk.message && chunk.message.content) {
                            this.messages[this.messages.length - 1].content += chunk.message.content
                            this.updateLastMessage()
                        }
                    } catch (e) { /* skip malformed chunks */ }
                }
            }

            this.autoSaveSession()
        } catch (e) {
            this.messages[this.messages.length - 1].content = `Error: ${e.message}`
            this.updateLastMessage()
        }

        this.isStreaming = false
        this.querySelector('#btn-send').disabled = false
        this.querySelector('#chat-input').focus()
    }

    renderMessages() {
        const container = this.querySelector('#chat-messages')
        container.innerHTML = this.messages.map((msg, i) => `
            <div class="message ${msg.role}">
                <div class="role-label">${msg.role === 'user' ? 'You' : this.currentModel}</div>
                <div class="message-content">${this.escapeHtml(msg.content)}${msg.role === 'assistant' && msg.content === '' ? '<span class="streaming-indicator"></span>' : ''}</div>
            </div>
        `).join('')
        container.scrollTop = container.scrollHeight
    }

    updateLastMessage() {
        const messages  = this.querySelectorAll('.message')
        const last      = messages[messages.length - 1]
        if (last) {
            const content = last.querySelector('.message-content')
            const msg     = this.messages[this.messages.length - 1]
            content.textContent = msg.content
        }
        const container = this.querySelector('#chat-messages')
        container.scrollTop = container.scrollHeight
    }

    escapeHtml(text) {
        const div = document.createElement('div')
        div.textContent = text
        return div.innerHTML
    }

    async autoSaveSession() {
        if (this.messages.length === 0) return
        try {
            const title = this.messages[0].content.substring(0, 50)
            const result = await llmAPI.saveSession(this.currentModel, title, this.messages)
            this.currentSessionId = result.id
            this.dispatchEvent(new CustomEvent('session-saved', { bubbles: true }))
        } catch (e) {
            console.warn('Could not save session:', e)
        }
    }

    loadSession(session) {
        this.currentSessionId = session.id
        this.currentModel     = session.model || this.currentModel
        this.messages         = session.messages || []
        this.renderMessages()
        const picker = this.querySelector('#model-picker')
        if (picker) {
            picker.value = this.currentModel
        }
    }

    newChat() {
        this.currentSessionId = null
        this.messages         = []
        this.renderMessages()
    }
}

customElements.define('chat-panel', ChatPanel)
