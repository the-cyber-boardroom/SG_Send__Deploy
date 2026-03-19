// ═══════════════════════════════════════════════════════════════════════════════
// Chat Panel — main chat interface with streaming responses
// Each instance is independent — supports multiple tabs via sg-layout
// ═══════════════════════════════════════════════════════════════════════════════

class ChatPanel extends HTMLElement {
    connectedCallback() {
        this.currentModel     = 'gemma3:4b'
        this.messages         = []
        this.currentSessionId = null
        this.isStreaming       = false
        this.abortController  = null
        this.pendingImages    = []                                           // base64 images queued for next send
        this.render()
        this.loadModels()

        // If sg-layout passed state with a sessionId, load that session
        if (this._pendingState && this._pendingState.sessionId) {
            this._loadSessionById(this._pendingState.sessionId)
            this._pendingState = null
        }
    }

    // sg-layout calls this before connectedCallback when creating from state
    setLayoutState(state) {
        if (state && state.sessionId) {
            if (this.isConnected) {
                this._loadSessionById(state.sessionId)
            } else {
                this._pendingState = state
            }
        }
    }

    // sg-layout calls this to serialize tab state
    getLayoutState() {
        return { sessionId: this.currentSessionId }
    }

    async _loadSessionById(sessionId) {
        try {
            const session = await llmAPI.getSession(sessionId)
            this.loadSession(session)
        } catch (e) {
            console.warn('Could not load session:', e)
        }
    }

    render() {
        this.innerHTML = `
            <div class="chat-panel">
                <div class="chat-header">
                    <select id="model-picker"></select>
                    <span id="chat-status" style="font-size:11px;color:var(--color-text-muted)"></span>
                </div>
                <div class="chat-messages" id="chat-messages"></div>
                <div class="chat-input-area">
                    <div class="image-preview-strip" id="image-previews"></div>
                    <textarea id="chat-input" placeholder="Type a message..." rows="1"></textarea>
                    <div class="chat-input-btns">
                        <button class="btn-attach" id="btn-attach" title="Attach image">&#x1F4CE;</button>
                        <button class="btn-send" id="btn-send">Send</button>
                        <button class="btn-stop" id="btn-stop" style="display:none">Stop</button>
                    </div>
                    <input type="file" id="file-input" accept="image/*" multiple style="display:none">
                </div>
            </div>`

        this.querySelector('#btn-send').addEventListener('click', () => this.sendMessage())
        this.querySelector('#btn-stop').addEventListener('click', () => this.stopStreaming())
        this.querySelector('#btn-attach').addEventListener('click', () => this.querySelector('#file-input').click())
        this.querySelector('#file-input').addEventListener('change', (e) => this.handleFileSelect(e))
        this.querySelector('#chat-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                this.sendMessage()
            }
        })
        this.querySelector('#chat-input').addEventListener('paste', (e) => this.handlePaste(e))
        this.querySelector('#model-picker').addEventListener('change', (e) => {
            this.currentModel = e.target.value
        })
    }

    // ── Image handling ──────────────────────────────────────────────────────

    handlePaste(e) {
        const items = e.clipboardData?.items
        if (!items) return

        for (const item of items) {
            if (item.type.startsWith('image/')) {
                e.preventDefault()
                const file = item.getAsFile()
                if (file) this.addImageFile(file)
            }
        }
    }

    handleFileSelect(e) {
        for (const file of e.target.files) {
            if (file.type.startsWith('image/')) {
                this.addImageFile(file)
            }
        }
        e.target.value = ''                                                  // reset so same file can be picked again
    }

    addImageFile(file) {
        const reader = new FileReader()
        reader.onload = () => {
            const base64 = reader.result.split(',')[1]                       // strip data:image/...;base64, prefix
            this.pendingImages.push(base64)
            this.renderImagePreviews()
        }
        reader.readAsDataURL(file)
    }

    renderImagePreviews() {
        const strip = this.querySelector('#image-previews')
        strip.innerHTML = this.pendingImages.map((b64, i) => `
            <div class="image-preview-item">
                <img src="data:image/png;base64,${b64}">
                <button class="remove-img" data-idx="${i}">&times;</button>
            </div>
        `).join('')

        strip.querySelectorAll('.remove-img').forEach(btn => {
            btn.addEventListener('click', () => {
                this.pendingImages.splice(parseInt(btn.dataset.idx), 1)
                this.renderImagePreviews()
            })
        })
    }

    // ── Models ──────────────────────────────────────────────────────────────

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

    // ── Send / Stop ─────────────────────────────────────────────────────────

    async sendMessage() {
        const input   = this.querySelector('#chat-input')
        const content = input.value.trim()
        if ((!content && this.pendingImages.length === 0) || this.isStreaming) return

        input.value     = ''
        this.isStreaming = true
        this.querySelector('#btn-send').style.display = 'none'
        this.querySelector('#btn-stop').style.display = ''

        // Build user message with optional images
        const userMsg = { role: 'user', content: content || '(image)' }
        if (this.pendingImages.length > 0) {
            userMsg.images = [...this.pendingImages]
            this.pendingImages = []
            this.renderImagePreviews()
        }

        this.messages.push(userMsg)
        this.renderMessages()

        this.messages.push({ role: 'assistant', content: '' })
        this.renderMessages()

        this.abortController = new AbortController()

        try {
            const apiMessages = this.messages.slice(0, -1).map(m => {
                const out = { role: m.role, content: m.content }
                if (m.images) out.images = m.images
                return out
            })
            const response = await llmAPI.chatStream(this.currentModel, apiMessages, this.abortController.signal)
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
            if (e.name === 'AbortError') {
                this.messages[this.messages.length - 1].content += '\n\n[stopped]'
            } else {
                this.messages[this.messages.length - 1].content = `Error: ${e.message}`
            }
            this.updateLastMessage()
        }

        this.isStreaming      = false
        this.abortController  = null
        this.querySelector('#btn-send').style.display = ''
        this.querySelector('#btn-stop').style.display = 'none'
        this.querySelector('#chat-input').focus()
    }

    stopStreaming() {
        if (this.abortController) {
            this.abortController.abort()
        }
    }

    // ── Rendering ───────────────────────────────────────────────────────────

    renderMessages() {
        const container = this.querySelector('#chat-messages')
        container.innerHTML = this.messages.map((msg, i) => {
            let imagesHtml = ''
            if (msg.images && msg.images.length > 0) {
                imagesHtml = `<div class="message-images">${
                    msg.images.map(b64 => `<img src="data:image/png;base64,${b64}">`).join('')
                }</div>`
            }
            const indicator = msg.role === 'assistant' && msg.content === ''
                ? '<span class="streaming-indicator"></span>'
                : ''
            return `<div class="message ${msg.role}">
                <div class="role-label">${msg.role === 'user' ? 'You' : this.currentModel}</div>
                ${imagesHtml}
                <div class="message-content">${this.escapeHtml(msg.content)}${indicator}</div>
            </div>`
        }).join('')
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

    // ── Session persistence ─────────────────────────────────────────────────

    async autoSaveSession() {
        if (this.messages.length === 0) return

        try {
            const title = this.messages[0].content.substring(0, 50)

            // Strip images from messages for storage (too large for session JSON)
            const storable = this.messages.map(m => ({ role: m.role, content: m.content }))

            if (this.currentSessionId) {
                // Update existing session
                await llmAPI.updateSession(this.currentSessionId, this.currentModel, title, storable)
            } else {
                // Create new session
                const result = await llmAPI.saveSession(this.currentModel, title, storable)
                this.currentSessionId = result.id
            }

            // Update the tab title in sg-layout
            this._updateTabTitle(title)

            this.dispatchEvent(new CustomEvent('session-saved', { bubbles: true }))
        } catch (e) {
            console.warn('Could not save session:', e)
        }
    }

    _updateTabTitle(title) {
        const layout = this._sgLayoutRef
        const panelId = this.dataset.panelId
        if (!layout || !panelId) return

        let tabNode = null
        layout._walkTabs(layout._tree, (t) => {
            if (t.id === panelId) tabNode = t
        })
        if (tabNode) {
            tabNode.title = title
            layout._updateStackTitle(tabNode)
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
