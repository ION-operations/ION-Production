# AIM-OS Mobile App – L4 Complete Reference (≈15,000 words)

**Level:** L4  
**System:** AIM-OS Mobile App  
**Status:** Planning  
**Updated:** 2025-11-01  
**Purpose:** Complete reference documentation

---

## 📚 **TABLE OF CONTENTS**

1. [Complete API Reference](#complete-api-reference)
2. [Component Specifications](#component-specifications)
3. [State Management Deep Dive](#state-management-deep-dive)
4. [Network Protocol Details](#network-protocol-details)
5. [Mobile UX Patterns](#mobile-ux-patterns)
6. [Performance Optimization](#performance-optimization)
7. [Security & Privacy](#security-privacy)
8. [Testing Strategy](#testing-strategy)
9. [Deployment Procedures](#deployment-procedures)
10. [Troubleshooting Guide](#troubleshooting-guide)

---

## 🔌 **COMPLETE API REFERENCE**

### **Extension Command Server Endpoints**

**Base URL:** `http://localhost:5001` (development) or configurable

#### **GET /health**
Health check endpoint.

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:5001
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2025-11-01T23:00:00Z"
}
```

#### **POST /mcp/execute**
Execute MCP tool.

**Request:**
```json
{
  "tool": "store_memory",
  "arguments": {
    "content": "Memory content",
    "tags": {"type": "note"},
    "metadata": {"source": "mobile"}
  }
}
```

**Response:**
```json
{
  "success": true,
  "tool": "store_memory",
  "result": {
    "success": true,
    "atom_id": "uuid",
    "message": "Stored memory"
  }
}
```

#### **GET /mcp/list**
List available MCP tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "store_memory",
      "description": "Store memory in CMC",
      "inputSchema": {...}
    }
  ]
}
```

### **MCP Tools Available**

**Core AIM-OS (6):**
- `store_memory` - Store in CMC
- `retrieve_memory` - Search HHNI
- `get_memory_stats` - Get statistics
- `create_plan` - Create APOE plan
- `track_confidence` - Track VIF confidence
- `synthesize_knowledge` - Synthesize SEG knowledge

**AI Collaboration (6):**
- `send_ai_message` - Send message to AI
- `get_ai_messages` - Get AI messages
- `start_ai_discussion` - Start discussion thread
- `handoff_task_to_ai` - Hand off task
- `share_ai_profile` - Share AI profile
- `get_ai_collaboration_summary` - Get summary

**Full list:** See `MCP_TOOLS_INVENTORY.md` (59 tools total)

---

## 🧩 **COMPONENT SPECIFICATIONS**

### **ChatScreen Component**

**Props:**
```typescript
interface ChatScreenProps {
  initialAgent?: string | null;
  onAgentChange?: (agent: string | null) => void;
}
```

**State:**
```typescript
interface ChatScreenState {
  selectedAgent: string | null;
  inputText: string;
  messages: AIMessage[];
  loading: boolean;
  error: string | null;
}
```

**Methods:**
- `handleSend()` - Send message
- `handleAgentSelect()` - Select agent
- `handleRefresh()` - Refresh messages

**Lifecycle:**
- Mount: Initialize chat hook, start polling
- Unmount: Stop polling, cleanup

### **MessageList Component**

**Props:**
```typescript
interface MessageListProps {
  messages: AIMessage[];
  onRefresh?: () => void;
  loading?: boolean;
}
```

**Features:**
- Virtualized list (FlatList)
- Auto-scroll to bottom
- Pull-to-refresh
- Infinite scroll (future)

### **ConnectionStatus Component**

**Props:**
```typescript
interface ConnectionStatusProps {
  showDetails?: boolean;
}
```

**Features:**
- Connection indicator
- Last check time
- Auto-reconnect
- Error display

---

## 🗄️ **STATE MANAGEMENT DEEP DIVE**

### **Chat Store**

**Store Definition:**
```typescript
interface ChatStore {
  messages: AIMessage[];
  threads: ChatThread[];
  agents: string[];
  selectedAgent: string | null;
  selectedThread: string | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  setMessages: (messages: AIMessage[]) => void;
  addMessage: (message: AIMessage) => void;
  selectAgent: (agent: string | null) => void;
  selectThread: (thread: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}
```

**Implementation:**
```typescript
import create from 'zustand';

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  threads: [],
  agents: [],
  selectedAgent: null,
  selectedThread: null,
  loading: false,
  error: null,
  
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  selectAgent: (agent) => set({ selectedAgent: agent }),
  selectThread: (thread) => set({ selectedThread: thread }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error })
}));
```

### **Connection Store**

**Store Definition:**
```typescript
interface ConnectionStore {
  connected: boolean;
  serverUrl: string;
  lastCheck: Date | null;
  reconnectAttempts: number;
  
  // Actions
  setConnected: (connected: boolean) => void;
  setServerUrl: (url: string) => void;
  checkConnection: () => Promise<boolean>;
  reconnect: () => Promise<void>;
}
```

---

## 📡 **NETWORK PROTOCOL DETAILS**

### **HTTP Client Configuration**

**Base Configuration:**
```typescript
const axiosConfig = {
  baseURL: 'http://localhost:5001',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
};
```

**Request Interceptor:**
```typescript
axios.interceptors.request.use(
  (config) => {
    // Add auth token (future)
    // Log request
    return config;
  },
  (error) => Promise.reject(error)
);
```

**Response Interceptor:**
```typescript
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors
    // Retry logic
    return Promise.reject(error);
  }
);
```

### **Polling Strategy**

**Efficient Polling:**
```typescript
class PollingManager {
  private interval: NodeJS.Timeout | null = null;
  private isPolling = false;
  
  start(callback: () => Promise<void>, intervalMs: number) {
    if (this.isPolling) return;
    
    this.isPolling = true;
    this.interval = setInterval(async () => {
      try {
        await callback();
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, intervalMs);
  }
  
  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    this.isPolling = false;
  }
}
```

**Adaptive Polling:**
- Active: 2 seconds
- Background: 10 seconds
- Offline: Stop polling

---

## 🎨 **MOBILE UX PATTERNS**

### **Navigation Patterns**

**Tab Navigation:**
- Bottom tabs for main sections
- Stack navigation for details
- Modal for settings

**Gesture Patterns:**
- Swipe to refresh
- Swipe to delete
- Long press for context menu
- Pull to load more

### **Loading States**

**Types:**
- Full screen loading
- Inline loading
- Skeleton screens
- Pull-to-refresh

**Implementation:**
```typescript
const LoadingStates = {
  idle: 'idle',
  loading: 'loading',
  success: 'success',
  error: 'error'
};
```

### **Error Handling**

**Error Types:**
- Network errors
- Server errors
- Validation errors
- Unknown errors

**Error Display:**
```typescript
<ErrorDisplay 
  error={error}
  onRetry={handleRetry}
  onDismiss={handleDismiss}
/>
```

---

## ⚡ **PERFORMANCE OPTIMIZATION**

### **List Optimization**

**FlatList Optimization:**
```typescript
<FlatList
  data={messages}
  renderItem={renderMessage}
  keyExtractor={extractKey}
  getItemLayout={getItemLayout} // Optimize scroll
  removeClippedSubviews={true} // Memory optimization
  maxToRenderPerBatch={10} // Batch rendering
  windowSize={10} // Window size
  initialNumToRender={20} // Initial render
/>
```

### **Memoization**

**Component Memoization:**
```typescript
export const MessageBubble = React.memo(({ message }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  return prevProps.message.message_id === nextProps.message.message_id;
});
```

**Hook Memoization:**
```typescript
const messages = useMemo(() => {
  return filteredMessages.sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
}, [filteredMessages]);
```

### **Image Optimization**

**Image Loading:**
```typescript
<Image
  source={{ uri: imageUrl }}
  resizeMode="cover"
  loadingIndicatorSource={placeholder}
  cache="force-cache"
/>
```

---

## 🔒 **SECURITY & PRIVACY**

### **Network Security**

**HTTPS (Production):**
```typescript
const apiConfig = {
  baseURL: 'https://api.aimos.com',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  }
};
```

**Certificate Pinning (Future):**
```typescript
// Future implementation
const certificatePinner = {
  'api.aimos.com': 'sha256/...'
};
```

### **Data Storage**

**Secure Storage:**
```typescript
import * as SecureStore from 'expo-secure-store';

// Store sensitive data
await SecureStore.setItemAsync('auth_token', token);

// Retrieve
const token = await SecureStore.getItemAsync('auth_token');
```

**Local Storage:**
```typescript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Store non-sensitive data
await AsyncStorage.setItem('user_preferences', JSON.stringify(prefs));

// Retrieve
const prefs = await AsyncStorage.getItem('user_preferences');
```

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests**

**Component Tests:**
```typescript
describe('ChatScreen', () => {
  it('renders correctly', () => {
    const { getByPlaceholderText } = render(<ChatScreen />);
    expect(getByPlaceholderText('Message all agents...')).toBeTruthy();
  });
  
  it('sends message on send', async () => {
    // Test implementation
  });
});
```

### **Integration Tests**

**API Integration:**
```typescript
describe('MCPAPI', () => {
  it('executes tool successfully', async () => {
    const api = new MCPAPI();
    const result = await api.executeTool('store_memory', {
      content: 'Test',
      tags: {}
    });
    expect(result.success).toBe(true);
  });
});
```

### **E2E Tests**

**App Flow:**
```typescript
describe('Chat Flow', () => {
  it('completes full chat flow', async () => {
    // Launch app
    // Navigate to chat
    // Send message
    // Verify response
  });
});
```

---

## 📦 **DEPLOYMENT PROCEDURES**

### **Development Build**

```bash
# Install dependencies
npm install

# Run Metro bundler
npx react-native start

# Run on Android
npx react-native run-android
```

### **Release Build**

```bash
# Generate release keystore
keytool -genkeypair -v -storetype PKCS12 -keystore release.keystore -alias release -keyalg RSA -keysize 2048 -validity 10000

# Build release APK
cd android
./gradlew assembleRelease

# APK location: android/app/build/outputs/apk/release/app-release.apk
```

### **Play Store Build**

```bash
# Build bundle
cd android
./gradlew bundleRelease

# Bundle location: android/app/build/outputs/bundle/release/app-release.aab
```

---

## 🔧 **TROUBLESHOOTING GUIDE**

### **Connection Issues**

**Problem:** Cannot connect to Command Server

**Solutions:**
1. Check server is running
2. Verify URL configuration
3. Check network connectivity
4. Verify firewall settings
5. Check AndroidManifest.xml permissions

**Debug Steps:**
```typescript
// Enable debug logging
console.log('Connection URL:', connectionManager.getCommandServerUrl());
console.log('Connection status:', await connectionManager.checkConnection());
```

### **Message Not Appearing**

**Problem:** Messages not showing in chat

**Solutions:**
1. Check polling is active
2. Verify message fetch succeeds
3. Check message filtering logic
4. Verify UI rendering
5. Check for errors in console

**Debug Steps:**
```typescript
// Check messages
console.log('Messages:', messages);
console.log('Loading:', loading);
console.log('Error:', error);
```

### **Performance Issues**

**Problem:** App is slow or laggy

**Solutions:**
1. Optimize FlatList rendering
2. Reduce polling frequency
3. Memoize components
4. Optimize images
5. Check for memory leaks

---

## 📊 **METRICS & MONITORING**

### **Key Metrics**

**Connection Metrics:**
- Connection success rate
- Average connection time
- Reconnection attempts

**Message Metrics:**
- Messages sent/received
- Average message delivery time
- Polling efficiency

**Performance Metrics:**
- App startup time
- Screen render time
- Memory usage
- Battery usage

### **Monitoring**

**Error Tracking:**
```typescript
import { Sentry } from '@sentry/react-native';

Sentry.init({
  dsn: 'YOUR_DSN',
  environment: __DEV__ ? 'development' : 'production'
});
```

**Analytics:**
```typescript
import analytics from '@react-native-firebase/analytics';

// Track events
await analytics().logEvent('message_sent', {
  agent: selectedAgent,
  message_length: message.length
});
```

---

## ✅ **COMPLETE FEATURE CHECKLIST**

### **Core Features**
- [x] Chat interface
- [x] Message polling
- [x] Agent discovery
- [x] Connection management
- [ ] Memory browser
- [ ] MCP tools UI
- [ ] Settings screen
- [ ] Offline support

### **Advanced Features**
- [ ] Push notifications
- [ ] Voice messages
- [ ] Image sharing
- [ ] File attachments
- [ ] Message search
- [ ] Thread management

### **Polish**
- [ ] Dark mode
- [ ] Animations
- [ ] Gestures
- [ ] Accessibility
- [ ] Internationalization

---

*L4 Complete Reference - AIM-OS Mobile App*  
*2025-11-01*

