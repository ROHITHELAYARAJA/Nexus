/**
 * Voice Recognition for NEXUS
 * Speech-to-text using Web Speech API
 */

class VoiceRecognition {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.isSupported = false;

        this.init();
    }

    init() {
        // Check browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.warn('Speech Recognition not supported in this browser');
            return;
        }

        this.isSupported = true;
        this.recognition = new SpeechRecognition();

        // Configure recognition
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';
        this.recognition.maxAlternatives = 1;

        // Event handlers
        this.recognition.onstart = () => {
            this.isListening = true;
            this.onStart();
        };

        this.recognition.onresult = (event) => {
            const last = event.results.length - 1;
            const transcript = event.results[last][0].transcript;
            const isFinal = event.results[last].isFinal;

            this.onResult(transcript, isFinal);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.onError(event.error);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.onEnd();
        };
    }

    start() {
        if (!this.isSupported) {
            alert('Voice recognition is not supported in your browser. Please use Chrome or Edge.');
            return false;
        }

        if (this.isListening) {
            this.stop();
            return false;
        }

        try {
            this.recognition.start();
            return true;
        } catch (error) {
            console.error('Failed to start recognition:', error);
            return false;
        }
    }

    stop() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    // Override these methods
    onStart() {
        console.log('Voice recognition started');
    }

    onResult(transcript, isFinal) {
        console.log('Transcript:', transcript, 'Final:', isFinal);
    }

    onError(error) {
        console.error('Voice recognition error:', error);
    }

    onEnd() {
        console.log('Voice recognition ended');
    }
}

// Create singleton instance
window.voiceRecognition = new VoiceRecognition();
