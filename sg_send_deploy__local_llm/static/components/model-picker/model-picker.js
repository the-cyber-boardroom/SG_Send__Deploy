// ═══════════════════════════════════════════════════════════════════════════════
// Model Picker — standalone model selector (for future use)
// ═══════════════════════════════════════════════════════════════════════════════

class ModelPicker extends HTMLElement {
    connectedCallback() {
        this.render()
    }

    render() {
        this.innerHTML = `<select id="model-select"></select>`
        this.loadModels()
    }

    async loadModels() {
        try {
            const models = await llmAPI.listModels()
            const select = this.querySelector('#model-select')
            select.innerHTML = models.map(m =>
                `<option value="${m.name}">${m.name} (${(m.size / 1e9).toFixed(1)}GB)</option>`
            ).join('')
        } catch (e) {
            console.warn('Could not load models:', e)
        }
    }
}

customElements.define('model-picker', ModelPicker)
