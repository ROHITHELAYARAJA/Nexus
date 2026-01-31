/**
 * Chat History Manager for NEXUS
 * Load, save, and manage conversation history
 */

class ChatHistory {
    constructor(apiBase = 'http://localhost:8080') {
        this.apiBase = apiBase;
        this.currentConversationId = null;
    }

    async getConversations(limit = 50) {
        try {
            const response = await fetch(`${this.apiBase}/history?limit=${limit}`);
            const data = await response.json();
            return data.conversations || [];
        } catch (error) {
            console.error('Failed to fetch conversations:', error);
            return [];
        }
    }

    async getConversation(id) {
        try {
            const response = await fetch(`${this.apiBase}/history/${id}`);
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch conversation:', error);
            return null;
        }
    }

    async createConversation(title, model = null) {
        try {
            const formData = new FormData();
            formData.append('title', title);
            if (model) formData.append('model', model);

            const response = await fetch(`${this.apiBase}/history/create`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            this.currentConversationId = data.id;
            return data;
        } catch (error) {
            console.error('Failed to create conversation:', error);
            return null;
        }
    }

    async addMessage(conversationId, role, content, model = null) {
        try {
            const formData = new FormData();
            formData.append('role', role);
            formData.append('content', content);
            if (model) formData.append('model', model);

            await fetch(`${this.apiBase}/history/${conversationId}/message`, {
                method: 'POST',
                body: formData
            });
        } catch (error) {
            console.error('Failed to add message:', error);
        }
    }

    async deleteConversation(id) {
        try {
            await fetch(`${this.apiBase}/history/${id}`, {
                method: 'DELETE'
            });
            return true;
        } catch (error) {
            console.error('Failed to delete conversation:', error);
            return false;
        }
    }

    async clearAll() {
        if (!confirm('Are you sure you want to delete all chat history?')) {
            return false;
        }

        try {
            await fetch(`${this.apiBase}/history`, {
                method: 'DELETE'
            });
            return true;
        } catch (error) {
            console.error('Failed to clear history:', error);
            return false;
        }
    }

    async search(query, limit = 20) {
        try {
            const response = await fetch(`${this.apiBase}/history/search/${encodeURIComponent(query)}?limit=${limit}`);
            const data = await response.json();
            return data.results || [];
        } catch (error) {
            console.error('Search failed:', error);
            return [];
        }
    }

    async exportToPDF(conversationId) {
        try {
            const response = await fetch(`${this.apiBase}/export/pdf/${conversationId}`);
            const blob = await response.blob();

            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `nexus_chat_${conversationId}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            return true;
        } catch (error) {
            console.error('PDF export failed:', error);
            return false;
        }
    }
}

// Create singleton
window.chatHistory = new ChatHistory();
