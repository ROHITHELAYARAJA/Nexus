/**
 * Settings Manager for NEXUS
 * Handles user preferences and configuration
 */

class SettingsManager {
    constructor() {
        this.settings = this.loadSettings();
    }

    getDefaults() {
        return {
            // Model settings
            defaultModel: 'auto',
            temperature: 0.7,
            maxTokens: 2048,

            // Voice settings
            voiceEnabled: true,
            voiceLanguage: 'en-US',
            autoListen: false,

            // UI settings
            theme: 'orbital_dark',
            backgroundEffects: true,
            animationSpeed: 1.0,
            fontSize: 'medium',

            // Chat settings
            autoSaveHistory: true,
            streamingEnabled: true,
            showModelBadge: true,
            showTimestamps: true,

            // Advanced
            showMetrics: false,
            developerMode: false
        };
    }

    loadSettings() {
        const stored = localStorage.getItem('nexus_settings');
        if (stored) {
            try {
                return { ...this.getDefaults(), ...JSON.parse(stored) };
            } catch (e) {
                console.error('Failed to parse settings:', e);
                return this.getDefaults();
            }
        }
        return this.getDefaults();
    }

    saveSettings() {
        localStorage.setItem('nexus_settings', JSON.stringify(this.settings));
        this.applySettings();
    }

    get(key) {
        return this.settings[key];
    }

    set(key, value) {
        this.settings[key] = value;
        this.saveSettings();
    }

    reset() {
        if (confirm('Reset all settings to defaults?')) {
            this.settings = this.getDefaults();
            this.saveSettings();
            return true;
        }
        return false;
    }

    export() {
        const dataStr = JSON.stringify(this.settings, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = 'nexus_settings.json';
        a.click();

        URL.revokeObjectURL(url);
    }

    async import(file) {
        try {
            const text = await file.text();
            const imported = JSON.parse(text);
            this.settings = { ...this.getDefaults(), ...imported };
            this.saveSettings();
            return true;
        } catch (e) {
            console.error('Failed to import settings:', e);
            alert('Invalid settings file');
            return false;
        }
    }

    applySettings() {
        // Apply background effects
        if (window.backgroundEffects) {
            window.backgroundEffects.toggle(this.settings.backgroundEffects);
        }

        // Apply font size
        document.documentElement.style.fontSize = {
            'small': '14px',
            'medium': '16px',
            'large': '18px'
        }[this.settings.fontSize] || '16px';

        // Apply metrics visibility
        const metricsPanel = document.getElementById('metrics-panel');
        if (metricsPanel) {
            metricsPanel.classList.toggle('hidden', !this.settings.showMetrics);
        }

        // Dispatch settings changed event
        window.dispatchEvent(new CustomEvent('settingsChanged', {
            detail: this.settings
        }));
    }
}

// Create singleton
window.settingsManager = new SettingsManager();

// Apply settings on load
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager.applySettings();
});
