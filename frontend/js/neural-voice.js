/**
 * Neural Voice Output for NEXUS
 * Uses Web Speech API for low-latency AI speech synthesis
 */

class NeuralVoice {
    constructor() {
        this.synth = window.speechSynthesis;
        this.voices = [];
        this.enabled = false;
        this.currentVoice = null;
        this.rate = 1.0;
        this.pitch = 1.0;

        if (this.synth) {
            this.loadVoices();
            if (this.synth.onvoiceschanged !== undefined) {
                this.synth.onvoiceschanged = () => this.loadVoices();
            }
        }
    }

    loadVoices() {
        this.voices = this.synth.getVoices();
        // Prefer natural sounding English voices
        this.currentVoice = this.voices.find(v => v.lang.includes('en') && v.name.includes('Google')) ||
            this.voices.find(v => v.lang.includes('en')) ||
            this.voices[0];
    }

    speak(text) {
        if (!this.enabled || !this.synth || !text) return;

        // Clean text (remove markdown-style artifacts for better speech)
        const cleanText = text.replace(/[*_`#]/g, '').replace(/\[Context attached:.*?\]/g, '');

        // Cancel any ongoing speech
        this.synth.cancel();

        const utterance = new SpeechSynthesisUtterance(cleanText);
        if (this.currentVoice) utterance.voice = this.currentVoice;
        utterance.rate = this.rate;
        utterance.pitch = this.pitch;

        utterance.onstart = () => {
            document.body.classList.add('ai-speaking');
            console.log('🎙️ AI is speaking...');
        };

        utterance.onend = () => {
            document.body.classList.remove('ai-speaking');
            console.log('🎙️ AI finished speaking.');
        };

        this.synth.speak(utterance);
    }

    stop() {
        if (this.synth) this.synth.cancel();
        document.body.classList.remove('ai-speaking');
    }

    setEnabled(state) {
        this.enabled = state;
        if (!state) this.stop();
    }

    setVoice(voiceName) {
        const voice = this.voices.find(v => v.name === voiceName);
        if (voice) this.currentVoice = voice;
    }
}

// Singleton
window.neuralVoice = new NeuralVoice();
