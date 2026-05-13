import * as assert from 'assert';
import * as vscode from 'vscode';
import { activate, deactivate } from '../extension';

suite('Extension Test Suite', () => {
    test('Extension should activate', async () => {
        const context = {
            extensionUri: vscode.Uri.file(__dirname),
            subscriptions: [],
            extension: {
                packageJSON: { version: '0.1.0' }
            }
        } as any;

        await activate(context);
        
        // Extension should be activated without errors
        assert.ok(true);
    });

    test('Extension should deactivate', () => {
        deactivate();
        
        // Extension should deactivate without errors
        assert.ok(true);
    });
});
