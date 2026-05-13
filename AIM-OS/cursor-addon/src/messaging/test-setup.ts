/**
 * Test Setup - Mock vscode module before any imports
 */

// Mock vscode module globally before any imports
const Module = require('module');
const originalRequire = Module.prototype.require;

Module.prototype.require = function(id: string) {
    if (id === 'vscode') {
        return {
            Uri: {
                file: (path: string) => ({ fsPath: path, scheme: 'file' }),
            },
            ExtensionContext: class {},
            workspace: {
                workspaceFolders: [
                    {
                        uri: {
                            fsPath: require('os').tmpdir(),
                        }
                    }
                ],
            },
        };
    }
    return originalRequire.apply(this, arguments);
};

// Now import the rest
export {};

