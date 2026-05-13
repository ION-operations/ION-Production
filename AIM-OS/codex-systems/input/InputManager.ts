/**
 * Input Manager System
 * Unified input handling for keyboard, mouse, gamepad, and touch
 * 
 * Features:
 * - Keyboard input with key bindings
 * - Mouse input with delta tracking
 * - Gamepad support (multiple)
 * - Touch input with gestures
 * - Input actions and bindings
 * - Customizable key mappings
 * - Input buffering
 * - Dead zones
 */

import * as THREE from 'three';

// ============================================
// TYPES
// ============================================

export type InputDevice = 'keyboard' | 'mouse' | 'gamepad' | 'touch';

export interface KeyBinding {
  action: string;
  keys: string[];
  modifiers?: ('ctrl' | 'shift' | 'alt')[];
}

export interface MouseState {
  position: THREE.Vector2;
  delta: THREE.Vector2;
  buttons: Set<number>;
  wheel: number;
  locked: boolean;
}

export interface TouchState {
  touches: Map<number, THREE.Vector2>;
  previousTouches: Map<number, THREE.Vector2>;
  pinchDistance: number;
  pinchDelta: number;
  swipeVelocity: THREE.Vector2;
}

export interface GamepadState {
  connected: boolean;
  index: number;
  axes: number[];
  buttons: boolean[];
  deadZone: number;
}

export interface InputAction {
  name: string;
  pressed: boolean;
  justPressed: boolean;
  justReleased: boolean;
  value: number;  // 0-1 for analog
  duration: number;  // Time held
}

// ============================================
// KEYBOARD HANDLER
// ============================================

export class KeyboardHandler {
  private keysDown: Set<string> = new Set();
  private keysPressed: Set<string> = new Set();
  private keysReleased: Set<string> = new Set();
  private modifiers = { ctrl: false, shift: false, alt: false };
  
  constructor() {
    this.setupListeners();
  }
  
  private setupListeners(): void {
    window.addEventListener('keydown', this.onKeyDown.bind(this));
    window.addEventListener('keyup', this.onKeyUp.bind(this));
    window.addEventListener('blur', this.onBlur.bind(this));
  }
  
  private onKeyDown(event: KeyboardEvent): void {
    const key = event.code;
    
    if (!this.keysDown.has(key)) {
      this.keysPressed.add(key);
    }
    this.keysDown.add(key);
    
    this.modifiers.ctrl = event.ctrlKey;
    this.modifiers.shift = event.shiftKey;
    this.modifiers.alt = event.altKey;
  }
  
  private onKeyUp(event: KeyboardEvent): void {
    const key = event.code;
    
    this.keysDown.delete(key);
    this.keysReleased.add(key);
    
    this.modifiers.ctrl = event.ctrlKey;
    this.modifiers.shift = event.shiftKey;
    this.modifiers.alt = event.altKey;
  }
  
  private onBlur(): void {
    this.keysDown.clear();
    this.modifiers = { ctrl: false, shift: false, alt: false };
  }
  
  public isKeyDown(key: string): boolean {
    return this.keysDown.has(key);
  }
  
  public isKeyPressed(key: string): boolean {
    return this.keysPressed.has(key);
  }
  
  public isKeyReleased(key: string): boolean {
    return this.keysReleased.has(key);
  }
  
  public getModifiers(): typeof this.modifiers {
    return { ...this.modifiers };
  }
  
  public update(): void {
    this.keysPressed.clear();
    this.keysReleased.clear();
  }
  
  public dispose(): void {
    window.removeEventListener('keydown', this.onKeyDown.bind(this));
    window.removeEventListener('keyup', this.onKeyUp.bind(this));
    window.removeEventListener('blur', this.onBlur.bind(this));
  }
}

// ============================================
// MOUSE HANDLER
// ============================================

export class MouseHandler {
  private state: MouseState;
  private element: HTMLElement;
  private previousPosition: THREE.Vector2;
  
  constructor(element: HTMLElement) {
    this.element = element;
    this.state = {
      position: new THREE.Vector2(),
      delta: new THREE.Vector2(),
      buttons: new Set(),
      wheel: 0,
      locked: false
    };
    this.previousPosition = new THREE.Vector2();
    
    this.setupListeners();
  }
  
  private setupListeners(): void {
    this.element.addEventListener('mousemove', this.onMouseMove.bind(this));
    this.element.addEventListener('mousedown', this.onMouseDown.bind(this));
    this.element.addEventListener('mouseup', this.onMouseUp.bind(this));
    this.element.addEventListener('wheel', this.onWheel.bind(this));
    this.element.addEventListener('contextmenu', (e) => e.preventDefault());
    
    document.addEventListener('pointerlockchange', this.onPointerLockChange.bind(this));
  }
  
  private onMouseMove(event: MouseEvent): void {
    if (this.state.locked) {
      this.state.delta.x += event.movementX;
      this.state.delta.y += event.movementY;
    } else {
      const rect = this.element.getBoundingClientRect();
      this.state.position.x = event.clientX - rect.left;
      this.state.position.y = event.clientY - rect.top;
      
      this.state.delta.x = this.state.position.x - this.previousPosition.x;
      this.state.delta.y = this.state.position.y - this.previousPosition.y;
    }
  }
  
  private onMouseDown(event: MouseEvent): void {
    this.state.buttons.add(event.button);
  }
  
  private onMouseUp(event: MouseEvent): void {
    this.state.buttons.delete(event.button);
  }
  
  private onWheel(event: WheelEvent): void {
    this.state.wheel += event.deltaY;
  }
  
  private onPointerLockChange(): void {
    this.state.locked = document.pointerLockElement === this.element;
  }
  
  public lockPointer(): void {
    this.element.requestPointerLock();
  }
  
  public unlockPointer(): void {
    document.exitPointerLock();
  }
  
  public getState(): MouseState {
    return {
      position: this.state.position.clone(),
      delta: this.state.delta.clone(),
      buttons: new Set(this.state.buttons),
      wheel: this.state.wheel,
      locked: this.state.locked
    };
  }
  
  public isButtonDown(button: number): boolean {
    return this.state.buttons.has(button);
  }
  
  public update(): void {
    this.previousPosition.copy(this.state.position);
    this.state.delta.set(0, 0);
    this.state.wheel = 0;
  }
  
  public dispose(): void {
    this.element.removeEventListener('mousemove', this.onMouseMove.bind(this));
    this.element.removeEventListener('mousedown', this.onMouseDown.bind(this));
    this.element.removeEventListener('mouseup', this.onMouseUp.bind(this));
    this.element.removeEventListener('wheel', this.onWheel.bind(this));
  }
}

// ============================================
// GAMEPAD HANDLER
// ============================================

export class GamepadHandler {
  private gamepads: Map<number, GamepadState> = new Map();
  private deadZone: number = 0.1;
  
  constructor(deadZone: number = 0.1) {
    this.deadZone = deadZone;
    this.setupListeners();
  }
  
  private setupListeners(): void {
    window.addEventListener('gamepadconnected', this.onGamepadConnected.bind(this));
    window.addEventListener('gamepaddisconnected', this.onGamepadDisconnected.bind(this));
  }
  
  private onGamepadConnected(event: GamepadEvent): void {
    console.log('Gamepad connected:', event.gamepad.id);
    
    this.gamepads.set(event.gamepad.index, {
      connected: true,
      index: event.gamepad.index,
      axes: [],
      buttons: [],
      deadZone: this.deadZone
    });
  }
  
  private onGamepadDisconnected(event: GamepadEvent): void {
    console.log('Gamepad disconnected:', event.gamepad.id);
    this.gamepads.delete(event.gamepad.index);
  }
  
  public update(): void {
    const gamepads = navigator.getGamepads();
    
    for (const gamepad of gamepads) {
      if (!gamepad) continue;
      
      const state = this.gamepads.get(gamepad.index);
      if (!state) continue;
      
      // Update axes with dead zone
      state.axes = gamepad.axes.map(axis => {
        if (Math.abs(axis) < this.deadZone) return 0;
        return axis;
      });
      
      // Update buttons
      state.buttons = gamepad.buttons.map(button => button.pressed);
    }
  }
  
  public getGamepad(index: number = 0): GamepadState | undefined {
    return this.gamepads.get(index);
  }
  
  public getAxis(gamepadIndex: number, axisIndex: number): number {
    const state = this.gamepads.get(gamepadIndex);
    return state?.axes[axisIndex] ?? 0;
  }
  
  public isButtonDown(gamepadIndex: number, buttonIndex: number): boolean {
    const state = this.gamepads.get(gamepadIndex);
    return state?.buttons[buttonIndex] ?? false;
  }
  
  public getConnectedCount(): number {
    return this.gamepads.size;
  }
  
  public dispose(): void {
    window.removeEventListener('gamepadconnected', this.onGamepadConnected.bind(this));
    window.removeEventListener('gamepaddisconnected', this.onGamepadDisconnected.bind(this));
  }
}

// ============================================
// TOUCH HANDLER
// ============================================

export class TouchHandler {
  private state: TouchState;
  private element: HTMLElement;
  
  constructor(element: HTMLElement) {
    this.element = element;
    this.state = {
      touches: new Map(),
      previousTouches: new Map(),
      pinchDistance: 0,
      pinchDelta: 0,
      swipeVelocity: new THREE.Vector2()
    };
    
    this.setupListeners();
  }
  
  private setupListeners(): void {
    this.element.addEventListener('touchstart', this.onTouchStart.bind(this), { passive: false });
    this.element.addEventListener('touchmove', this.onTouchMove.bind(this), { passive: false });
    this.element.addEventListener('touchend', this.onTouchEnd.bind(this));
    this.element.addEventListener('touchcancel', this.onTouchEnd.bind(this));
  }
  
  private onTouchStart(event: TouchEvent): void {
    event.preventDefault();
    this.updateTouches(event.touches);
  }
  
  private onTouchMove(event: TouchEvent): void {
    event.preventDefault();
    this.updateTouches(event.touches);
    
    // Calculate pinch
    if (event.touches.length >= 2) {
      const touch1 = new THREE.Vector2(event.touches[0].clientX, event.touches[0].clientY);
      const touch2 = new THREE.Vector2(event.touches[1].clientX, event.touches[1].clientY);
      const newDistance = touch1.distanceTo(touch2);
      
      this.state.pinchDelta = newDistance - this.state.pinchDistance;
      this.state.pinchDistance = newDistance;
    }
    
    // Calculate swipe velocity
    if (event.touches.length === 1) {
      const touch = event.touches[0];
      const current = new THREE.Vector2(touch.clientX, touch.clientY);
      const prev = this.state.previousTouches.get(touch.identifier);
      
      if (prev) {
        this.state.swipeVelocity.copy(current).sub(prev);
      }
    }
  }
  
  private onTouchEnd(event: TouchEvent): void {
    this.updateTouches(event.touches);
    
    if (event.touches.length < 2) {
      this.state.pinchDistance = 0;
      this.state.pinchDelta = 0;
    }
  }
  
  private updateTouches(touchList: TouchList): void {
    // Store previous
    this.state.previousTouches = new Map(this.state.touches);
    this.state.touches.clear();
    
    for (let i = 0; i < touchList.length; i++) {
      const touch = touchList[i];
      const rect = this.element.getBoundingClientRect();
      
      this.state.touches.set(touch.identifier, new THREE.Vector2(
        touch.clientX - rect.left,
        touch.clientY - rect.top
      ));
    }
  }
  
  public getState(): TouchState {
    return {
      touches: new Map(this.state.touches),
      previousTouches: new Map(this.state.previousTouches),
      pinchDistance: this.state.pinchDistance,
      pinchDelta: this.state.pinchDelta,
      swipeVelocity: this.state.swipeVelocity.clone()
    };
  }
  
  public getTouchCount(): number {
    return this.state.touches.size;
  }
  
  public getTouch(index: number): THREE.Vector2 | undefined {
    const entries = Array.from(this.state.touches.values());
    return entries[index]?.clone();
  }
  
  public update(): void {
    this.state.swipeVelocity.set(0, 0);
    this.state.pinchDelta = 0;
  }
  
  public dispose(): void {
    this.element.removeEventListener('touchstart', this.onTouchStart.bind(this));
    this.element.removeEventListener('touchmove', this.onTouchMove.bind(this));
    this.element.removeEventListener('touchend', this.onTouchEnd.bind(this));
    this.element.removeEventListener('touchcancel', this.onTouchEnd.bind(this));
  }
}

// ============================================
// INPUT MANAGER
// ============================================

export class InputManager {
  private keyboard: KeyboardHandler;
  private mouse: MouseHandler;
  private gamepad: GamepadHandler;
  private touch: TouchHandler;
  
  private bindings: Map<string, KeyBinding> = new Map();
  private actions: Map<string, InputAction> = new Map();
  private actionStartTimes: Map<string, number> = new Map();
  
  constructor(element: HTMLElement) {
    this.keyboard = new KeyboardHandler();
    this.mouse = new MouseHandler(element);
    this.gamepad = new GamepadHandler();
    this.touch = new TouchHandler(element);
    
    this.setupDefaultBindings();
  }
  
  private setupDefaultBindings(): void {
    // Common game bindings
    this.addBinding({ action: 'moveForward', keys: ['KeyW', 'ArrowUp'] });
    this.addBinding({ action: 'moveBackward', keys: ['KeyS', 'ArrowDown'] });
    this.addBinding({ action: 'moveLeft', keys: ['KeyA', 'ArrowLeft'] });
    this.addBinding({ action: 'moveRight', keys: ['KeyD', 'ArrowRight'] });
    this.addBinding({ action: 'jump', keys: ['Space'] });
    this.addBinding({ action: 'crouch', keys: ['ControlLeft', 'KeyC'] });
    this.addBinding({ action: 'sprint', keys: ['ShiftLeft'] });
    this.addBinding({ action: 'interact', keys: ['KeyE', 'KeyF'] });
    this.addBinding({ action: 'pause', keys: ['Escape'] });
  }
  
  /**
   * Add key binding
   */
  public addBinding(binding: KeyBinding): void {
    this.bindings.set(binding.action, binding);
    
    // Initialize action
    if (!this.actions.has(binding.action)) {
      this.actions.set(binding.action, {
        name: binding.action,
        pressed: false,
        justPressed: false,
        justReleased: false,
        value: 0,
        duration: 0
      });
    }
  }
  
  /**
   * Remove binding
   */
  public removeBinding(action: string): void {
    this.bindings.delete(action);
    this.actions.delete(action);
  }
  
  /**
   * Update all input
   */
  public update(deltaTime: number): void {
    // Update handlers
    this.gamepad.update();
    
    // Update actions
    for (const [actionName, binding] of this.bindings) {
      const action = this.actions.get(actionName)!;
      const wasPressed = action.pressed;
      
      // Check keyboard
      let pressed = false;
      for (const key of binding.keys) {
        if (this.keyboard.isKeyDown(key)) {
          pressed = true;
          break;
        }
      }
      
      // Check modifiers
      if (pressed && binding.modifiers) {
        const mods = this.keyboard.getModifiers();
        for (const mod of binding.modifiers) {
          if (!mods[mod]) {
            pressed = false;
            break;
          }
        }
      }
      
      // Update action state
      action.justPressed = pressed && !wasPressed;
      action.justReleased = !pressed && wasPressed;
      action.pressed = pressed;
      action.value = pressed ? 1 : 0;
      
      // Track duration
      if (action.justPressed) {
        this.actionStartTimes.set(actionName, performance.now());
      }
      
      if (pressed && this.actionStartTimes.has(actionName)) {
        action.duration = (performance.now() - this.actionStartTimes.get(actionName)!) / 1000;
      } else {
        action.duration = 0;
      }
    }
    
    // Update input handlers (clear per-frame state)
    this.keyboard.update();
    this.mouse.update();
    this.touch.update();
  }
  
  /**
   * Get action state
   */
  public getAction(action: string): InputAction | undefined {
    return this.actions.get(action);
  }
  
  /**
   * Check if action is pressed
   */
  public isActionPressed(action: string): boolean {
    return this.actions.get(action)?.pressed ?? false;
  }
  
  /**
   * Check if action was just pressed
   */
  public isActionJustPressed(action: string): boolean {
    return this.actions.get(action)?.justPressed ?? false;
  }
  
  /**
   * Check if action was just released
   */
  public isActionJustReleased(action: string): boolean {
    return this.actions.get(action)?.justReleased ?? false;
  }
  
  /**
   * Get movement input (WASD/Arrows + Gamepad)
   */
  public getMovementInput(): THREE.Vector2 {
    const input = new THREE.Vector2();
    
    // Keyboard
    if (this.isActionPressed('moveForward')) input.y += 1;
    if (this.isActionPressed('moveBackward')) input.y -= 1;
    if (this.isActionPressed('moveLeft')) input.x -= 1;
    if (this.isActionPressed('moveRight')) input.x += 1;
    
    // Gamepad (left stick)
    const gamepad = this.gamepad.getGamepad(0);
    if (gamepad) {
      input.x += gamepad.axes[0] ?? 0;
      input.y -= gamepad.axes[1] ?? 0;
    }
    
    // Touch (virtual joystick would go here)
    
    // Normalize
    if (input.length() > 1) {
      input.normalize();
    }
    
    return input;
  }
  
  /**
   * Get look input (mouse delta + gamepad right stick)
   */
  public getLookInput(): THREE.Vector2 {
    const input = new THREE.Vector2();
    
    // Mouse
    const mouse = this.mouse.getState();
    input.x += mouse.delta.x;
    input.y += mouse.delta.y;
    
    // Gamepad (right stick)
    const gamepad = this.gamepad.getGamepad(0);
    if (gamepad) {
      input.x += (gamepad.axes[2] ?? 0) * 10;
      input.y += (gamepad.axes[3] ?? 0) * 10;
    }
    
    return input;
  }
  
  /**
   * Get mouse state
   */
  public getMouse(): MouseState {
    return this.mouse.getState();
  }
  
  /**
   * Get touch state
   */
  public getTouch(): TouchState {
    return this.touch.getState();
  }
  
  /**
   * Get gamepad state
   */
  public getGamepad(index: number = 0): GamepadState | undefined {
    return this.gamepad.getGamepad(index);
  }
  
  /**
   * Lock mouse pointer
   */
  public lockPointer(): void {
    this.mouse.lockPointer();
  }
  
  /**
   * Unlock mouse pointer
   */
  public unlockPointer(): void {
    this.mouse.unlockPointer();
  }
  
  /**
   * Dispose
   */
  public dispose(): void {
    this.keyboard.dispose();
    this.mouse.dispose();
    this.gamepad.dispose();
    this.touch.dispose();
    this.bindings.clear();
    this.actions.clear();
  }
}

