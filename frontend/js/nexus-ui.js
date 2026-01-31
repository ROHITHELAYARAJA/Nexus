/**
 * NEXUS UI V2.0 - Ultra Premium Intelligence Interface
 * Stability-First Architecture
 */

class NexusUI {
    constructor() {
        this.apiBase = 'http://localhost:8080';
        this.isStreaming = false;

        // Modules
        this.history = window.chatHistory;
        this.voice = window.voiceRecognition;
        this.files = window.fileManager;
        this.settings = window.settingsManager;

        // All elements must match index.html EXACTLY
        this.elements = {
            chatMessages: document.getElementById('chat-messages'),
            chatInput: document.getElementById('chat-input'),
            sendBtn: document.getElementById('send-btn'),

            // Sidebar
            historyList: document.getElementById('history-list'),
            historySearch: document.getElementById('history-search'),
            newChat: document.getElementById('new-chat'),
            settingsToggle: document.getElementById('settings-toggle'),

            // Header & Context
            modelSelector: document.getElementById('model-selector'),
            metricsToggle: document.getElementById('metrics-toggle'),
            metricsPanel: document.getElementById('metrics-panel'),
            activeModelDisplay: document.getElementById('active-model-display'),
            exportPdfBtn: document.getElementById('export-pdf-btn'),
            clearHistory: document.getElementById('clear-history'),

            // Actions
            voiceBtn: document.getElementById('voice-btn'),
            fileUploadBtn: document.getElementById('file-upload-btn'),
            fileInput: document.getElementById('file-input'),

            // Modals & Settings
            settingsModal: document.getElementById('settings-modal'),
            closeSettings: document.getElementById('close-settings'),
            saveSettings: document.getElementById('save-settings'),
            resetSettings: document.getElementById('reset-settings'),
            tempSlider: document.getElementById('temp-slider'),
            tempValue: document.getElementById('temp-value'),
            clearAllHistory: document.getElementById('setting-clear-all'),

            // Toast
            statusToast: document.getElementById('status-toast'),
            toastMessage: document.getElementById('toast-message')
        };

        this.init().catch(err => {
            console.error('CRITICAL INITIALIZATION ERROR:', err);
            this.showToast('❌ System Initialization Failed');
        });
    }

    async init() {
        console.log('🚀 NEXUS V2.0 Booting...');

        this.verifyElements();
        this.setupEventListeners();
        this.setupModuleIntegrations();
        this.setupSettingsTabs();

        await this.loadInitialData();
        this.startHealthPolling();
        this.setupNeuralBackground();

        console.log('✅ NEXUS V2.0 Online');
    }

    verifyElements() {
        for (const [name, el] of Object.entries(this.elements)) {
            if (!el && name !== 'activeModelDisplay') { // modelBadge replaced by modelSelector in some logic
                console.warn(`⚠️ Warning: UI Element "${name}" not found in DOM!`);
            }
        }
    }

    setupEventListeners() {
        // Chat Actions
        if (this.elements.sendBtn) {
            this.elements.sendBtn.addEventListener('click', () => this.handleSendMessage());
        }

        if (this.elements.chatInput) {
            this.elements.chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSendMessage();
                }
            });

            this.elements.chatInput.addEventListener('input', () => {
                this.updateInputUI();
                this.autoResizeTextarea();
            });
        }

        // Navigation & Actions
        if (this.elements.newChat) {
            this.elements.newChat.addEventListener('click', () => this.createNewSession());
        }

        if (this.elements.settingsToggle) {
            this.elements.settingsToggle.addEventListener('click', () => this.toggleModal('settingsModal'));
        }

        if (this.elements.closeSettings) {
            this.elements.closeSettings.addEventListener('click', () => this.toggleModal('settingsModal', false));
        }

        if (this.elements.metricsToggle) {
            this.elements.metricsToggle.addEventListener('click', () => {
                if (this.elements.metricsPanel) this.elements.metricsPanel.classList.toggle('hidden');
            });
        }

        if (this.elements.clearHistory) {
            this.elements.clearHistory.addEventListener('click', () => this.handleClearHistory());
        }

        if (this.elements.clearAllHistory) {
            this.elements.clearAllHistory.addEventListener('click', () => this.handleClearHistory());
        }

        if (this.elements.saveSettings) {
            this.elements.saveSettings.addEventListener('click', () => {
                this.applyAdvancedSettings();
                this.toggleModal('settingsModal', false);
                this.showToast('⚙️ System Config Updated');
            });
        }

        if (this.elements.exportPdfBtn) {
            this.elements.exportPdfBtn.addEventListener('click', () => this.handleExportPDF());
        }

        if (this.elements.tempSlider) {
            this.elements.tempSlider.oninput = (e) => {
                const val = e.target.value / 10;
                if (this.elements.tempValue) this.elements.tempValue.textContent = val;
            };
        }

        if (this.elements.modelSelector) {
            this.elements.modelSelector.addEventListener('change', (e) => {
                this.showToast(`🤖 Model context switched to: ${e.target.value}`);
            });
        }

        // Advanced Selectors
        const fontSelector = document.getElementById('setting-font-family');
        if (fontSelector) {
            fontSelector.addEventListener('change', (e) => {
                document.body.style.setProperty('--font-main', e.target.value);
                document.body.style.fontFamily = e.target.value;
            });
        }

        const voiceToggle = document.getElementById('setting-voice-output');
        if (voiceToggle) {
            voiceToggle.addEventListener('change', (e) => {
                if (window.neuralVoice) window.neuralVoice.setEnabled(e.target.checked);
            });
        }

        // Modal Close on backdrop
        window.addEventListener('click', (e) => {
            if (e.target === document.getElementById('settings-overlay')) {
                this.toggleModal('settingsModal', false);
            }
        });
    }

    applyAdvancedSettings() {
        // This would normally save to localStorage or backend
        const family = document.getElementById('setting-font-family')?.value;
        if (family) {
            document.body.style.fontFamily = family;
        }

        const voiceEnabled = document.getElementById('setting-voice-output')?.checked;
        if (window.neuralVoice) window.neuralVoice.setEnabled(voiceEnabled);
    }

    setupSettingsTabs() {
        const tabs = document.querySelectorAll('.tab-btn');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.getAttribute('data-tab');

                // Update buttons
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // Update content
                document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
                document.getElementById(target).classList.remove('hidden');
            });
        });
    }

    async handleClearHistory() {
        if (this.history && await this.history.clearAll()) {
            this.elements.chatMessages.innerHTML = '';
            this.renderWelcome();
            this.loadSessions();
            this.showToast('🗑️ Neural Cache Cleared');
        }
    }

    setupModuleIntegrations() {
        // Re-check modules if they were missed in constructor
        this.history = this.history || window.chatHistory;
        this.voice = this.voice || window.voiceRecognition;
        this.files = this.files || window.fileManager;
        this.settings = this.settings || window.settingsManager;

        console.log('🔗 Integrating Modules:', {
            history: !!this.history,
            voice: !!this.voice,
            files: !!this.files
        });

        // Voice Recognition (STT)
        if (this.voice && this.elements.voiceBtn) {
            this.elements.voiceBtn.onclick = () => {
                console.log('🎙️ Voice Button Clicked');
                if (this.voice.isListening) {
                    this.voice.stop();
                } else {
                    const started = this.voice.start();
                    if (started) this.elements.voiceBtn.classList.add('active');
                }
            };

            this.voice.onStart = () => {
                this.elements.voiceBtn.classList.add('active');
                this.showToast('🎤 Neural Listening Active');
            };

            this.voice.onResult = (text, final) => {
                if (this.elements.chatInput) {
                    this.elements.chatInput.value += (this.elements.chatInput.value ? ' ' : '') + text;
                    this.autoResizeTextarea();
                    this.updateInputUI();
                }
            };

            this.voice.onEnd = () => {
                this.elements.voiceBtn.classList.remove('active');
            };

            this.voice.onError = (err) => {
                console.error('Voice Error:', err);
                this.showToast(`❌ Voice Error: ${err}`);
                this.elements.voiceBtn.classList.remove('active');
            };
        } else {
            console.warn('⚠️ Voice Recognition module or button missing');
        }

        // Neural Voice (TTS)
        if (window.neuralVoice) {
            console.log('🔊 Neural Voice (TTS) Ready');
            const ttsToggle = document.getElementById('setting-voice-output');
            if (ttsToggle) window.neuralVoice.setEnabled(ttsToggle.checked);
        }

        // File Integration
        if (this.files && this.elements.fileUploadBtn) {
            this.elements.fileUploadBtn.onclick = () => this.elements.fileInput.click();
            this.elements.fileInput.onchange = async (e) => {
                const files = e.target.files;
                if (!files.length) return;
                this.showToast('⌛ Uploading Intelligence...');
                for (const file of files) {
                    const res = await this.files.uploadFile(file);
                    if (res.success) {
                        this.elements.chatInput.value += `\n[Context attached: ${res.filename}]\n`;
                        this.autoResizeTextarea();
                        this.updateInputUI();
                    }
                }
                this.elements.fileInput.value = '';
            };
        }

        // History Integration
        if (this.elements.historySearch) {
            this.elements.historySearch.oninput = (e) => this.debounce(() => this.searchSessions(e.target.value), 300)();
        }
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadModels(),
                this.loadSessions(),
                this.checkHealth()
            ]);
        } catch (e) { console.error('Initial load load error', e); }
    }

    async loadModels() {
        try {
            const res = await fetch(`${this.apiBase}/models`);
            const data = await res.json();

            if (data && data.models) {
                const selectors = [this.elements.modelSelector, document.getElementById('setting-default-model')];

                selectors.forEach(selector => {
                    if (!selector) return;

                    // Clear existing options
                    selector.innerHTML = '';

                    data.models.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.name;
                        option.textContent = `${model.name} (${model.role})`;
                        selector.appendChild(option);
                    });
                });

                console.log(`📡 Loaded ${data.models.length} Neural Cores`);
            }
        } catch (e) {
            console.error('Failed to load models:', e);
        }
    }

    updateInputUI() {
        const hasText = this.elements.chatInput.value.trim().length > 0;
        if (this.elements.sendBtn) this.elements.sendBtn.disabled = !hasText || this.isStreaming;
    }

    autoResizeTextarea() {
        const area = this.elements.chatInput;
        if (!area) return;
        area.style.height = 'auto';
        area.style.height = Math.min(area.scrollHeight, 200) + 'px';
    }

    async handleSendMessage() {
        const query = this.elements.chatInput.value.trim();
        if (!query || this.isStreaming) return;

        this.isStreaming = true;
        this.updateInputUI();

        // Stop any ongoing speech when user starts a new query
        if (window.neuralVoice) window.neuralVoice.stop();

        // Reset input immediately
        this.elements.chatInput.value = '';
        this.autoResizeTextarea();

        // Get selected model
        const model = this.elements.modelSelector ? this.elements.modelSelector.value : 'auto';

        // Ensure we have a conversation context
        if (!this.history.currentConversationId) {
            const title = query.substring(0, 30) + (query.length > 30 ? '...' : '');
            const newSession = await this.history.createConversation(title, model !== 'auto' ? model : null);
            if (newSession) {
                this.history.currentConversationId = newSession.id;
                this.loadSessions(); // Refresh sidebar
            }
        }

        // Add user message to UI and Persistence
        await this.history.addMessage(this.history.currentConversationId, 'user', query);
        this.appendMessage('user', query);

        try {
            const assistantId = this.addPlaceholderResponse();
            let fullText = '';
            let actualModel = '';

            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: query,
                    stream: true,
                    model: model !== 'auto' ? model : undefined
                })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.type === 'content') {
                                fullText += data.content;
                                this.updatePlaceholder(assistantId, fullText);
                            } else if (data.type === 'model_selected') {
                                actualModel = data.model;
                                this.updateModelDisplay(data.model);
                            }
                        } catch (e) { }
                    }
                }
            }

            // AI Voice Output after stream completes
            if (window.neuralVoice) {
                window.neuralVoice.speak(fullText);
            }

            // Save Assistant message
            await this.history.addMessage(this.history.currentConversationId, 'assistant', fullText, actualModel);

        } catch (error) {
            console.error('Stream failed', error);
            this.showToast('❌ Transmission Encrypted/Failed');
        } finally {
            this.isStreaming = false;
            this.updateInputUI();
        }
    }

    appendMessage(role, content) {
        const msgId = `msg-${Date.now()}`;
        const avatar = role === 'user' ? 'UR' : 'NX';
        const html = `
            <div class="message ${role}" id="${msgId}">
                <div class="avatar">${avatar}</div>
                <div class="message-content">
                    <div class="message-text">${this.renderMarkdown(content)}</div>
                    <div class="message-meta">${new Date().toLocaleTimeString()}</div>
                </div>
            </div>
        `;

        this.clearEmptyState();
        this.elements.chatMessages.insertAdjacentHTML('beforeend', html);
        this.highlightCode(msgId);
        this.scrollToBottom();
    }

    addPlaceholderResponse() {
        const id = `ai-${Date.now()}`;
        const html = `
            <div class="message assistant" id="${id}">
                <div class="avatar">NX</div>
                <div class="message-content">
                    <div class="message-text" id="${id}-text">
                        <div class="typing"><span></span><span></span><span></span></div>
                    </div>
                </div>
            </div>
        `;
        this.elements.chatMessages.insertAdjacentHTML('beforeend', html);
        this.scrollToBottom();
        return id;
    }

    updatePlaceholder(id, content) {
        const el = document.getElementById(`${id}-text`);
        if (el) {
            el.innerHTML = this.renderMarkdown(content);
            this.highlightCode(id);
            this.scrollToBottom();
        }
    }

    async loadSessions() {
        if (!this.history) return;
        const sessions = await this.history.getConversations();
        if (!this.elements.historyList) return;

        this.elements.historyList.innerHTML = sessions.map(s => `
            <div class="history-item ${this.history.currentConversationId === s.id ? 'active' : ''}" 
                 onclick="window.nexusUI.openSession(${s.id})">
                <span class="history-item-title">${s.title}</span>
                <button class="delete-session-btn" onclick="event.stopPropagation(); window.nexusUI.deleteSpecificSession(${s.id})">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"></path><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            </div>
        `).join('');
    }

    async deleteSpecificSession(id) {
        if (confirm('Delete this neural session?')) {
            if (await this.history.deleteConversation(id)) {
                if (this.history.currentConversationId === id) {
                    this.createNewSession();
                }
                this.loadSessions();
                this.showToast('🗑️ Session Purged');
            }
        }
    }

    async openSession(id) {
        if (this.isStreaming) return;
        const session = await this.history.getConversation(id);
        if (session) {
            this.history.currentConversationId = id;
            this.elements.chatMessages.innerHTML = '';
            session.messages.forEach(m => this.appendMessage(m.role, m.content));
            this.loadSessions();
        }
    }

    createNewSession() {
        if (this.isStreaming) return;
        this.history.currentConversationId = null;
        this.elements.chatMessages.innerHTML = `
            <div class="empty-state">
                <div class="nexus-logo-anim"><div class="ring"></div><div class="core"></div></div>
                <h1>New Session Initialized</h1>
                <p>Deploy query to proceed.</p>
            </div>
        `;
        this.loadSessions();
    }

    renderWelcome() {
        this.elements.chatMessages.innerHTML = `
            <div class="empty-state">
                <div class="nexus-logo-anim"><div class="ring"></div><div class="core"></div></div>
                <h1>What can NEXUS solve for you?</h1>
                <p>Specialized models are indexed and ready for deployment.</p>
            </div>
        `;
    }

    handleExportPDF() {
        if (!this.history.currentConversationId) return this.showToast('❌ No session to export');
        this.history.exportToPDF(this.history.currentConversationId);
    }

    // UTILITIES
    renderMarkdown(text) {
        return typeof marked !== 'undefined' ? marked.parse(text) : text;
    }

    highlightCode(id) {
        const block = document.getElementById(id);
        if (block && window.hljs) {
            block.querySelectorAll('pre code').forEach(c => hljs.highlightElement(c));
        }
    }

    scrollToBottom() {
        this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
    }

    clearEmptyState() {
        const empty = this.elements.chatMessages.querySelector('.empty-state');
        if (empty) empty.remove();
    }

    toggleModal(name, show = true) {
        const modal = this.elements[name];
        if (modal) modal.classList.toggle('hidden', !show);
    }

    showToast(msg) {
        if (!this.elements.statusToast) return;
        this.elements.toastMessage.textContent = msg;
        this.elements.statusToast.classList.remove('hidden');
        setTimeout(() => this.elements.statusToast.classList.add('hidden'), 4000);
    }

    async checkHealth() {
        try {
            const res = await fetch(`${this.apiBase}/health`);
            const data = await res.json();
            if (data.status === 'healthy') {
                this.updateModelDisplay('Neural Network Online');
            }
        } catch (e) {
            this.updateModelDisplay('System Offline');
        }
    }

    updateModelDisplay(text) {
        if (this.elements.activeModelDisplay) {
            this.elements.activeModelDisplay.textContent = text;
        }
    }

    startHealthPolling() {
        setInterval(() => {
            fetch(`${this.apiBase}/metrics`).then(r => r.json()).then(d => {
                const cpu = document.getElementById('cpu-bar');
                const mem = document.getElementById('memory-bar');
                if (cpu) cpu.style.width = d.system.cpu.usage_percent + '%';
                if (mem) mem.style.width = d.system.memory.percent + '%';
            }).catch(() => { });
        }, 5000);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    setupNeuralBackground() {
        if (window.backgroundEffects) {
            window.backgroundEffects.init();
        }
    }
}

// Global Initialization
document.addEventListener('DOMContentLoaded', () => {
    window.nexusUI = new NexusUI();
});
