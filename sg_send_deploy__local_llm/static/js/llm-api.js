// ═══════════════════════════════════════════════════════════════════════════════
// LLM API Client — fetch wrapper for all API calls
// ═══════════════════════════════════════════════════════════════════════════════

class LlmAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl
    }

    async fetch(path, options = {}) {
        const response = await fetch(`${this.baseUrl}${path}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        })
        return response
    }

    async chatStream(model, messages) {                                     // POST /api/chat — returns ReadableStream
        const response = await this.fetch('/api/chat/chat', {
            method : 'POST',
            body   : JSON.stringify({ model, messages, stream: true })
        })
        return response
    }

    async listModels() {                                                    // GET /api/models
        const response = await this.fetch('/api/models/models')
        const data     = await response.json()
        return data.models || []
    }

    async listSessions() {                                                  // GET /api/sessions
        const response = await this.fetch('/api/sessions/sessions')
        return response.json()
    }

    async getSession(id) {                                                  // GET /api/sessions/{id}
        const response = await this.fetch(`/api/sessions/sessions/${id}`)
        return response.json()
    }

    async saveSession(model, title, messages) {                             // POST /api/sessions
        const response = await this.fetch('/api/sessions/create', {
            method : 'POST',
            body   : JSON.stringify({ model, title, messages })
        })
        return response.json()
    }

    async deleteSession(id) {                                               // DELETE /api/sessions/{id}
        const response = await this.fetch(`/api/sessions/delete/${id}`, {
            method: 'DELETE'
        })
        return response.json()
    }
}

const llmAPI = new LlmAPI()
