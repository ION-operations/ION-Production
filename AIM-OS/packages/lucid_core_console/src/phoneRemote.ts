import { DaemonClient } from './daemonClient';
import { TimelineLogger } from './timelineLogger';
import * as crypto from 'crypto';

export interface PhonePairingInfo {
    qrCode: string;
    pairingCode: string;
    expiresAt: number;
    sessionId: string;
}

export interface PhoneSession {
    sessionId: string;
    deviceId: string;
    deviceName: string;
    privilegeTier: 'observer' | 'planner' | 'approver';
    connectedAt: number;
    lastActivity: number;
}

export class PhoneRemote {
    private _daemonClient: DaemonClient;
    private _timelineLogger: TimelineLogger;
    private _activePairings: Map<string, PhonePairingInfo> = new Map();
    private _activeSessions: Map<string, PhoneSession> = new Map();
    private _pairingTimeout: number = 300000; // 5 minutes

    constructor(daemonClient: DaemonClient, timelineLogger: TimelineLogger) {
        this._daemonClient = daemonClient;
        this._timelineLogger = timelineLogger;
    }

    public async startPairing(): Promise<string> {
        const pairingId = this._generatePairingId();
        const qrCode = this._generateQRCode(pairingId);
        const pairingCode = this._generatePairingCode();
        const sessionId = this._generateSessionId();

        const pairingInfo: PhonePairingInfo = {
            qrCode: qrCode,
            pairingCode: pairingCode,
            expiresAt: Date.now() + this._pairingTimeout,
            sessionId: sessionId
        };

        this._activePairings.set(pairingId, pairingInfo);

        // Set up cleanup timer
        setTimeout(() => {
            this._cleanupExpiredPairing(pairingId);
        }, this._pairingTimeout);

        this._timelineLogger.log('phone_pairing_started', {
            pairingId: pairingId,
            qrCode: qrCode,
            pairingCode: pairingCode,
            expiresAt: pairingInfo.expiresAt,
            timestamp: Date.now()
        });

        return qrCode;
    }

    public async completePairing(pairingId: string, deviceInfo: {
        deviceId: string;
        deviceName: string;
        privilegeTier: 'observer' | 'planner' | 'approver';
    }): Promise<PhoneSession> {
        const pairing = this._activePairings.get(pairingId);
        if (!pairing) {
            throw new Error('Invalid or expired pairing ID');
        }

        if (Date.now() > pairing.expiresAt) {
            this._activePairings.delete(pairingId);
            throw new Error('Pairing has expired');
        }

        const session: PhoneSession = {
            sessionId: pairing.sessionId,
            deviceId: deviceInfo.deviceId,
            deviceName: deviceInfo.deviceName,
            privilegeTier: deviceInfo.privilegeTier,
            connectedAt: Date.now(),
            lastActivity: Date.now()
        };

        this._activeSessions.set(session.sessionId, session);
        this._activePairings.delete(pairingId);

        this._timelineLogger.log('phone_pairing_completed', {
            pairingId: pairingId,
            sessionId: session.sessionId,
            deviceId: deviceInfo.deviceId,
            deviceName: deviceInfo.deviceName,
            privilegeTier: deviceInfo.privilegeTier,
            timestamp: Date.now()
        });

        return session;
    }

    public async disconnectSession(sessionId: string): Promise<void> {
        const session = this._activeSessions.get(sessionId);
        if (session) {
            this._activeSessions.delete(sessionId);
            
            this._timelineLogger.log('phone_session_disconnected', {
                sessionId: sessionId,
                deviceId: session.deviceId,
                deviceName: session.deviceName,
                timestamp: Date.now()
            });
        }
    }

    public async sendCommand(sessionId: string, command: {
        type: string;
        data: any;
    }): Promise<any> {
        const session = this._activeSessions.get(sessionId);
        if (!session) {
            throw new Error('Session not found');
        }

        // Update last activity
        session.lastActivity = Date.now();

        // Check privilege level
        if (!this._hasPermission(session, command.type)) {
            throw new Error('Insufficient privileges for this command');
        }

        this._timelineLogger.log('phone_command_received', {
            sessionId: sessionId,
            deviceId: session.deviceId,
            commandType: command.type,
            privilegeTier: session.privilegeTier,
            timestamp: Date.now()
        });

        // Process command based on type
        switch (command.type) {
            case 'voiceInput':
                return await this._handleVoiceInput(session, command.data);
            case 'approveChange':
                return await this._handleApproveChange(session, command.data);
            case 'forceEdit':
                return await this._handleForceEdit(session, command.data);
            case 'getStatus':
                return await this._handleGetStatus(session);
            default:
                throw new Error(`Unknown command type: ${command.type}`);
        }
    }

    private async _handleVoiceInput(session: PhoneSession, data: any): Promise<any> {
        // Process voice input from phone
        const response = await this._daemonClient.processInput(data.text);
        
        this._timelineLogger.log('phone_voice_input_processed', {
            sessionId: session.sessionId,
            deviceId: session.deviceId,
            input: data.text,
            responseType: response.type,
            timestamp: Date.now()
        });

        return response;
    }

    private async _handleApproveChange(session: PhoneSession, data: any): Promise<any> {
        await this._daemonClient.approveChange(data.changeId);
        
        this._timelineLogger.log('phone_change_approved', {
            sessionId: session.sessionId,
            deviceId: session.deviceId,
            changeId: data.changeId,
            timestamp: Date.now()
        });

        return { success: true };
    }

    private async _handleForceEdit(session: PhoneSession, data: any): Promise<any> {
        await this._daemonClient.forceEdit(data.changeId);
        
        this._timelineLogger.log('phone_change_forced', {
            sessionId: session.sessionId,
            deviceId: session.deviceId,
            changeId: data.changeId,
            timestamp: Date.now()
        });

        return { success: true };
    }

    private async _handleGetStatus(session: PhoneSession): Promise<any> {
        const status = {
            connected: this._daemonClient.isConnected,
            activeSessions: this._activeSessions.size,
            privilegeTier: session.privilegeTier,
            lastActivity: session.lastActivity
        };

        this._timelineLogger.log('phone_status_requested', {
            sessionId: session.sessionId,
            deviceId: session.deviceId,
            status: status,
            timestamp: Date.now()
        });

        return status;
    }

    private _hasPermission(session: PhoneSession, commandType: string): boolean {
        switch (session.privilegeTier) {
            case 'observer':
                return ['getStatus'].includes(commandType);
            case 'planner':
                return ['getStatus', 'voiceInput'].includes(commandType);
            case 'approver':
                return ['getStatus', 'voiceInput', 'approveChange', 'forceEdit'].includes(commandType);
            default:
                return false;
        }
    }

    private _generatePairingId(): string {
        return `pairing_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    private _generateQRCode(pairingId: string): string {
        // In a real implementation, this would generate an actual QR code
        // For now, we'll return a base64 encoded string
        const data = `lucid://pair?id=${pairingId}`;
        return Buffer.from(data).toString('base64');
    }

    private _generatePairingCode(): string {
        // Generate a 6-digit pairing code
        return Math.floor(100000 + Math.random() * 900000).toString();
    }

    private _generateSessionId(): string {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    private _cleanupExpiredPairing(pairingId: string): void {
        const pairing = this._activePairings.get(pairingId);
        if (pairing && Date.now() > pairing.expiresAt) {
            this._activePairings.delete(pairingId);
            
            this._timelineLogger.log('phone_pairing_expired', {
                pairingId: pairingId,
                timestamp: Date.now()
            });
        }
    }

    public getActiveSessions(): PhoneSession[] {
        return Array.from(this._activeSessions.values());
    }

    public getActivePairings(): PhonePairingInfo[] {
        return Array.from(this._activePairings.values());
    }

    public cleanup(): void {
        // Clean up expired pairings
        const now = Date.now();
        for (const [pairingId, pairing] of this._activePairings.entries()) {
            if (now > pairing.expiresAt) {
                this._activePairings.delete(pairingId);
            }
        }

        // Clean up inactive sessions (older than 1 hour)
        const oneHourAgo = now - 3600000;
        for (const [sessionId, session] of this._activeSessions.entries()) {
            if (session.lastActivity < oneHourAgo) {
                this._activeSessions.delete(sessionId);
            }
        }

        this._timelineLogger.log('phone_remote_cleanup', {
            activeSessions: this._activeSessions.size,
            activePairings: this._activePairings.size,
            timestamp: Date.now()
        });
    }

    public dispose(): void {
        this._activePairings.clear();
        this._activeSessions.clear();
    }
}
