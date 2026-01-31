/**
 * File Manager for NEXUS
 * Handle file uploads and processing
 */

class FileManager {
    constructor(apiBase = 'http://localhost:8080') {
        this.apiBase = apiBase;
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.apiBase}/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('File upload error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    async uploadMultiple(files) {
        const results = [];

        for (const file of files) {
            const result = await this.uploadFile(file);
            results.push(result);
        }

        return results;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();

        const icons = {
            'pdf': '📄',
            'docx': '📝',
            'doc': '📝',
            'txt': '📃',
            'md': '📋',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️',
            'gif': '🖼️',
            'py': '🐍',
            'js': '📜',
            'json': '📊',
            'yaml': '⚙️',
            'yml': '⚙️'
        };

        return icons[ext] || '📎';
    }

    isImage(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(ext);
    }
}

// Create singleton
window.fileManager = new FileManager();
