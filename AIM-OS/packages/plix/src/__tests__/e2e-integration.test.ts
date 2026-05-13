/**
 * End-to-End Integration Tests
 * 
 * Tests the complete PLIX quaternion extension pipeline:
 * 1. Parse PLIX → AST
 * 2. Type check → Validated AST
 * 3. Compile → Syscalls (with tag resolution via HHNI/SEG)
 * 4. Execute → Runtime (with kernel bridge + CMC + SEG tracking)
 */

import { PLIXParser } from '../parser';
import { PLIXQuaternionCompiler } from '../compiler/quaternion-compiler';
import { PLIXQuaternionRuntime } from '../runtime/quaternion-runtime';
import { RustKernelBridge } from '../runtime/rust-kernel-bridge';
import { CMCStorageClient, MockCMCStorage } from '../runtime/cmc-storage-client';
import { HHNIHTTPClient, MockHHNIClient } from '../compiler/hhni-client';
import { SEGHTTPClient, MockSEGClient } from '../compiler/seg-client';
import { DefaultFieldSolver } from '../runtime/quaternion-runtime';

describe('End-to-End Integration Tests', () => {
  let parser: PLIXParser;
  let compiler: PLIXQuaternionCompiler;
  let runtime: PLIXQuaternionRuntime;
  let mockHHNI: MockHHNIClient;
  let mockSEG: MockSEGClient;
  let mockCMC: MockCMCStorage;

  beforeEach(() => {
    // Initialize mock clients
    mockHHNI = new MockHHNIClient();
    mockSEG = new MockSEGClient();
    mockCMC = new MockCMCStorage();

    // Register test tag → QAddr mapping
    mockHHNI.registerTag('@test.entity', {
      type: 'qaddr',
      n: 1,
      l: 'memory',
      m: 0,
      s: 'plan',
      morton_key: 12345,
      s3_bin: 6789,
    });

    // Initialize parser
    parser = new PLIXParser();

    // Initialize compiler with mock clients
    compiler = new PLIXQuaternionCompiler({
      hhniClient: mockHHNI,
      segClient: mockSEG,
      cmcClient: mockCMC,
    });

    // Initialize runtime with mock components
    runtime = new PLIXQuaternionRuntime({
      kernelBridge: new RustKernelBridge('http://localhost:8080/api/kernel/v1'),
      cmcStorage: mockCMC,
      fieldSolver: new DefaultFieldSolver(),
      segClient: mockSEG,
      actorQAddr: {
        type: 'qaddr',
        n: 1,
        l: 'io',
        s: 'act',
      },
    });
  });

  describe('Complete Pipeline: Parse → Type Check → Compile → Execute', () => {
    it('should execute place syscall end-to-end', async () => {
      // 1. Parse PLIX
      const plixText = `
        with Q(n:1, l:memory, s:plan) do
          place @test.entity at (x:0.1, y:0.0, z:0.0, τ:now) ori:⟨+k,0°⟩
      `;

      const intent = parser.parse(plixText);
      expect(intent.geometric).toBeDefined();
      expect(intent.geometric?.operations).toHaveLength(1);

      // 2. Compile to syscalls
      const compilationResult = await compiler.compileGeometricOperations(
        intent.geometric!.operations
      );

      expect(compilationResult.syscalls).toHaveLength(1);
      expect(compilationResult.syscalls[0].type).toBe('place');
      expect(compilationResult.syscalls[0].qaddr).toBeDefined();

      // 3. Execute syscall
      const executionResult = await runtime.executeSyscall(compilationResult.syscalls[0]);

      expect(executionResult.success).toBe(true);
      expect(executionResult.entityId).toBe('test.entity');
    });

    it('should execute move syscall end-to-end', async () => {
      // First place entity
      const placeText = `
        with Q(n:1, l:memory, s:plan) do
          place @test.entity at (x:0.1, y:0.0, z:0.0, τ:now) ori:⟨+k,0°⟩
      `;
      const placeIntent = parser.parse(placeText);
      const placeCompilation = await compiler.compileGeometricOperations(
        placeIntent.geometric!.operations
      );
      await runtime.executeSyscall(placeCompilation.syscalls[0]);

      // Then move entity
      const moveText = `
        with Q(n:1, l:memory, s:act) do
          move @test.entity Δpose: dq(screw_axis=+k, θ=5°, t=2cm)
      `;
      const moveIntent = parser.parse(moveText);
      const moveCompilation = await compiler.compileGeometricOperations(
        moveIntent.geometric!.operations
      );

      expect(moveCompilation.syscalls).toHaveLength(1);
      expect(moveCompilation.syscalls[0].type).toBe('move');

      const executionResult = await runtime.executeSyscall(moveCompilation.syscalls[0]);

      expect(executionResult.success).toBe(true);
      expect(executionResult.qaddr).toBeDefined();
    });

    it('should execute sense syscall end-to-end', async () => {
      // Place entity first
      const placeText = `
        with Q(n:1, l:memory, s:plan) do
          place @test.entity at (x:0.1, y:0.0, z:0.0, τ:now) ori:⟨+k,0°⟩
      `;
      const placeIntent = parser.parse(placeText);
      const placeCompilation = await compiler.compileGeometricOperations(
        placeIntent.geometric!.operations
      );
      await runtime.executeSyscall(placeCompilation.syscalls[0]);

      // Then sense
      const senseText = `
        with Q(n:1, l:memory, s:read) do
          sense region: sphere(center: (x:0.1, y:0.0, z:0.0), radius: 1.0)
      `;
      const senseIntent = parser.parse(senseText);
      const senseCompilation = await compiler.compileGeometricOperations(
        senseIntent.geometric!.operations
      );

      expect(senseCompilation.syscalls).toHaveLength(1);
      expect(senseCompilation.syscalls[0].type).toBe('sense');

      const executionResult = await runtime.executeSyscall(senseCompilation.syscalls[0]);

      expect(executionResult.success).toBe(true);
      expect(executionResult.result?.entities).toBeDefined();
    });

    it('should execute emit syscall end-to-end', async () => {
      // Place entity first
      const placeText = `
        with Q(n:1, l:memory, s:plan) do
          place @test.entity at (x:0.1, y:0.0, z:0.0, τ:now) ori:⟨+k,0°⟩
      `;
      const placeIntent = parser.parse(placeText);
      const placeCompilation = await compiler.compileGeometricOperations(
        placeIntent.geometric!.operations
      );
      await runtime.executeSyscall(placeCompilation.syscalls[0]);

      // Then emit
      const emitText = `
        with Q(n:1, l:memory, s:write) do
          emit @test.entity event: "field_update" effect: {kappa: 0.1}
      `;
      const emitIntent = parser.parse(emitText);
      const emitCompilation = await compiler.compileGeometricOperations(
        emitIntent.geometric!.operations
      );

      expect(emitCompilation.syscalls).toHaveLength(1);
      expect(emitCompilation.syscalls[0].type).toBe('emit');

      const executionResult = await runtime.executeSyscall(emitCompilation.syscalls[0]);

      expect(executionResult.success).toBe(true);
    });
  });

  describe('Tag Resolution Pipeline', () => {
    it('should resolve tag via HHNI', async () => {
      const result = await compiler.resolveTagToQAddr('@test.entity');

      expect(result.qaddr).toBeDefined();
      expect(result.source).toBe('hhni');
      expect(result.confidence).toBeGreaterThan(0.8);
    });

    it('should fallback to SEG if HHNI fails', async () => {
      // Register tag in SEG instead
      await mockSEG.trackEntityCreation('test.entity', {
        type: 'qaddr',
        n: 1,
        l: 'memory',
        m: 0,
        s: 'plan',
        morton_key: 99999,
        s3_bin: 88888,
      }, '@test.entity');

      // Clear HHNI mapping
      mockHHNI = new MockHHNIClient();
      compiler = new PLIXQuaternionCompiler({
        hhniClient: mockHHNI,
        segClient: mockSEG,
      });

      const result = await compiler.resolveTagToQAddr('@test.entity');

      expect(result.qaddr).toBeDefined();
      expect(result.source).toBe('seg');
    });
  });

  describe('Provenance Tracking', () => {
    it('should track entity creation in SEG', async () => {
      const plixText = `
        with Q(n:1, l:memory, s:plan) do
          place @test.entity at (x:0.1, y:0.0, z:0.0, τ:now) ori:⟨+k,0°⟩
      `;

      const intent = parser.parse(plixText);
      const compilationResult = await compiler.compileGeometricOperations(
        intent.geometric!.operations
      );
      await runtime.executeSyscall(compilationResult.syscalls[0]);

      // Check SEG tracking
      const lineage = await mockSEG.getEntityLineage('test.entity');
      expect(lineage.length).toBeGreaterThan(0);
    });

    it('should track syscall execution in SEG', async () => {
      const plixText = `
        with Q(n:1, l:memory, s:plan) do
          place @test.entity at (x:0.1, y:0.0, z:0.0, τ:now) ori:⟨+k,0°⟩
      `;

      const intent = parser.parse(plixText);
      const compilationResult = await compiler.compileGeometricOperations(
        intent.geometric!.operations
      );
      await runtime.executeSyscall(compilationResult.syscalls[0]);

      // Check relations
      const relations = await mockSEG.getEntityRelations('test.entity');
      expect(relations.length).toBeGreaterThan(0);
    });
  });

  describe('CMC Storage Integration', () => {
    it('should store entity state in CMC', async () => {
      const plixText = `
        with Q(n:1, l:memory, s:plan) do
          place @test.entity at (x:0.1, y:0.0, z:0.0, τ:now) ori:⟨+k,0°⟩
      `;

      const intent = parser.parse(plixText);
      const compilationResult = await compiler.compileGeometricOperations(
        intent.geometric!.operations
      );
      await runtime.executeSyscall(compilationResult.syscalls[0]);

      // Check CMC storage
      const entity = await mockCMC.retrieveEntity('test.entity');
      expect(entity).toBeDefined();
      expect(entity?.qaddr).toBeDefined();
    });
  });
});

