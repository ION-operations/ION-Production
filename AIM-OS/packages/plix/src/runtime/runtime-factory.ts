/**
 * Example: Using Real Rust Kernel Bridge
 * 
 * Demonstrates how to configure PLIX runtime with real Rust kernel bridge
 */

import { PLIXQuaternionRuntime } from './quaternion-runtime';
import { RustKernelBridge } from './rust-kernel-bridge';
import { DefaultKernelBridge, DefaultFieldSolver } from './quaternion-runtime';
import { CMCStorageClient, MockCMCStorage } from './cmc-storage-client';
import type { CMCStorage } from './quaternion-runtime';

/**
 * Create runtime with real Rust kernel bridge and CMC storage
 */
export function createRuntimeWithRealKernel(
  kernelServerUrl: string = 'http://localhost:8080/api/kernel/v1',
  cmcServerUrl: string = 'http://localhost:5000/api/cmc/v1',
  actorQAddr?: any
): PLIXQuaternionRuntime {
  // Create real kernel bridge
  const kernelBridge = new RustKernelBridge(kernelServerUrl);
  
  // Create real CMC storage client
  const cmcStorage = new CMCStorageClient(cmcServerUrl);
  
  // Create runtime with real bridge and storage
  return new PLIXQuaternionRuntime({
    kernelBridge: kernelBridge,
    cmcStorage: cmcStorage,
    fieldSolver: new DefaultFieldSolver(),
    actorQAddr: actorQAddr || {
      type: 'qaddr',
      n: 1,
      l: 'io',
      s: 'act',
    },
  });
}

/**
 * Create runtime with real Rust kernel bridge and custom CMC storage
 */
export function createRuntimeWithRealKernelAndCustomCMC(
  kernelServerUrl: string = 'http://localhost:8080/api/kernel/v1',
  cmcStorage: CMCStorage,
  actorQAddr?: any
): PLIXQuaternionRuntime {
  // Create real kernel bridge
  const kernelBridge = new RustKernelBridge(kernelServerUrl);
  
  // Create runtime with real bridge and custom storage
  return new PLIXQuaternionRuntime({
    kernelBridge: kernelBridge,
    cmcStorage: cmcStorage,
    fieldSolver: new DefaultFieldSolver(),
    actorQAddr: actorQAddr || {
      type: 'qaddr',
      n: 1,
      l: 'io',
      s: 'act',
    },
  });
}

/**
 * Create runtime with default (placeholder) bridge
 * 
 * Useful for testing without Rust kernel server
 */
export function createRuntimeWithDefaultBridge(
  cmcStorage?: CMCStorage,
  actorQAddr?: any
): PLIXQuaternionRuntime {
  return new PLIXQuaternionRuntime({
    kernelBridge: new DefaultKernelBridge(),
    cmcStorage: cmcStorage || new MockCMCStorage(),
    fieldSolver: new DefaultFieldSolver(),
    actorQAddr: actorQAddr || {
      type: 'qaddr',
      n: 1,
      l: 'io',
      s: 'act',
    },
  });
}

