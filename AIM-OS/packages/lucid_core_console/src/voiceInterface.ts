import { DaemonClient } from './daemonClient';
import { TimelineLogger } from './timelineLogger';

export interface VoiceConfig {
    language: string;
    continuous: boolean;
    interimResults: boolean;
    maxAlternatives: number;
}

export class VoiceInterface {
    private _daemonClient: DaemonClient;
    private _timelineLogger: TimelineLogger;
    private _isListening: boolean = false;
    private _recognition?: any;
    private _config: VoiceConfig;

    constructor(daemonClient: DaemonClient, timelineLogger: TimelineLogger) {
        this._daemonClient = daemonClient;
        this._timelineLogger = timelineLogger;
        this._config = {
            language: 'en-US',
            continuous: false,
            interimResults: true,
            maxAlternatives: 1
        };
        
        this._initializeSpeechRecognition();
    }

    private _initializeSpeechRecognition() {
        // Check if speech recognition is available
        if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
            const SpeechRecognition = (window as any).webkitSpeechRecognition;
            this._recognition = new SpeechRecognition();
            this._setupRecognition();
        } else if (typeof window !== 'undefined' && 'SpeechRecognition' in window) {
            const SpeechRecognition = (window as any).SpeechRecognition;
            this._recognition = new SpeechRecognition();
            this._setupRecognition();
        } else {
            this._timelineLogger.log('speech_recognition_not_available', {
                timestamp: Date.now()
            });
        }
    }

    private _setupRecognition() {
        if (!this._recognition) return;

        this._recognition.continuous = this._config.continuous;
        this._recognition.interimResults = this._config.interimResults;
        this._recognition.lang = this._config.language;
        this._recognition.maxAlternatives = this._config.maxAlternatives;

        this._recognition.onstart = () => {
            this._isListening = true;
            this._timelineLogger.log('voice_recognition_started', {
                timestamp: Date.now()
            });
        };

        this._recognition.onend = () => {
            this._isListening = false;
            this._timelineLogger.log('voice_recognition_ended', {
                timestamp: Date.now()
            });
        };

        this._recognition.onerror = (event: any) => {
            this._isListening = false;
            this._timelineLogger.log('voice_recognition_error', {
                error: event.error,
                timestamp: Date.now()
            });
        };

        this._recognition.onresult = (event: any) => {
            this._handleRecognitionResult(event);
        };
    }

    private _handleRecognitionResult(event: any) {
        const results = event.results;
        const result = results[results.length - 1];
        
        if (result.isFinal) {
            const transcript = result[0].transcript;
            const confidence = result[0].confidence;
            
            this._timelineLogger.log('voice_recognition_result', {
                transcript: transcript,
                confidence: confidence,
                timestamp: Date.now()
            });

            // Send to daemon for processing
            this._daemonClient.processInput(transcript);
        }
    }

    public async startListening(): Promise<void> {
        if (!this._recognition) {
            throw new Error('Speech recognition not available');
        }

        if (this._isListening) {
            throw new Error('Already listening');
        }

        try {
            this._recognition.start();
            this._timelineLogger.log('voice_listening_started', {
                timestamp: Date.now()
            });
        } catch (error) {
            this._timelineLogger.log('voice_listening_start_failed', {
                error: error.message,
                timestamp: Date.now()
            });
            throw error;
        }
    }

    public async stopListening(): Promise<void> {
        if (!this._recognition) {
            throw new Error('Speech recognition not available');
        }

        if (!this._isListening) {
            throw new Error('Not currently listening');
        }

        try {
            this._recognition.stop();
            this._timelineLogger.log('voice_listening_stopped', {
                timestamp: Date.now()
            });
        } catch (error) {
            this._timelineLogger.log('voice_listening_stop_failed', {
                error: error.message,
                timestamp: Date.now()
            });
            throw error;
        }
    }

    public async processAudio(audioData: string): Promise<string> {
        // This would typically involve sending audio data to a speech-to-text service
        // For now, we'll simulate processing
        this._timelineLogger.log('audio_processing_started', {
            audioDataLength: audioData.length,
            timestamp: Date.now()
        });

        // Simulate processing delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // In a real implementation, this would call a speech-to-text API
        const transcript = "Simulated transcript from audio data";
        
        this._timelineLogger.log('audio_processing_completed', {
            transcript: transcript,
            timestamp: Date.now()
        });

        return transcript;
    }

    public get isListening(): boolean {
        return this._isListening;
    }

    public updateConfig(config: Partial<VoiceConfig>): void {
        this._config = { ...this._config, ...config };
        
        if (this._recognition) {
            this._setupRecognition();
        }

        this._timelineLogger.log('voice_config_updated', {
            config: this._config,
            timestamp: Date.now()
        });
    }

    public getConfig(): VoiceConfig {
        return { ...this._config };
    }

    public dispose(): void {
        if (this._recognition && this._isListening) {
            this._recognition.stop();
        }
        this._recognition = undefined;
        this._isListening = false;
    }
}
