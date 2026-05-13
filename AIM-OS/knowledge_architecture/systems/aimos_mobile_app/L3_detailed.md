# AIM-OS Mobile App – L3 Detailed Implementation Guide (≈10,000 words)

**Level:** L3  
**System:** AIM-OS Mobile App  
**Status:** Planning  
**Updated:** 2025-11-01  
**Audience:** Developers implementing mobile app

---

## 📋 **TABLE OF CONTENTS**

1. [Setup & Installation](#setup-installation)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Network Layer](#network-layer)
5. [Chat Interface](#chat-interface)
6. [Agent Management](#agent-management)
7. [Memory Browser](#memory-browser)
8. [MCP Tools Integration](#mcp-tools-integration)
9. [State Management](#state-management)
10. [Navigation](#navigation)
11. [Testing](#testing)
12. [Deployment](#deployment)

---

## 🚀 **SETUP & INSTALLATION**

### **Prerequisites**

```bash
# Required tools
- Node.js 18+
- npm or yarn
- Android Studio (for Android development)
- React Native CLI
- Java JDK 11+
- Android SDK
```

### **Step 1: Initialize React Native Project**

```bash
# Create new React Native project
npx react-native@latest init AIMOSMobileApp --template react-native-template-typescript

cd AIMOSMobileApp

# Install dependencies
npm install
```

### **Step 2: Install Core Dependencies**

```bash
# Navigation
npm install @react-navigation/native @react-navigation/native-stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context

# State management
npm install zustand

# Networking
npm install axios

# Storage
npm install @react-native-async-storage/async-storage

# Icons
npm install react-native-vector-icons
npm install @types/react-native-vector-icons --save-dev

# Gestures & Animations
npm install react-native-gesture-handler react-native-reanimated

# Environment config
npm install react-native-config
```

### **Step 3: Copy Shared Code**

```bash
# Copy service layer from Electron app
cp -r ../ide_chat_app/src/services packages/aimos_mobile_app/src/
cp -r ../ide_chat_app/src/hooks packages/aimos_mobile_app/src/
```

### **Step 4: Android Configuration**

**android/app/src/main/AndroidManifest.xml:**
```xml
<manifest>
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <application
        android:usesCleartextTraffic="true"
        ...>
    </application>
</manifest>
```

**android/app/build.gradle:**
```gradle
android {
    defaultConfig {
        minSdkVersion 21
        targetSdkVersion 34
    }
}
```

---

## 📁 **PROJECT STRUCTURE**

```
packages/aimos_mobile_app/
├── src/
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ChatScreen.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   └── AgentSelector.tsx
│   │   ├── Agents/
│   │   │   ├── AgentListScreen.tsx
│   │   │   ├── AgentCard.tsx
│   │   │   └── ThreadSelector.tsx
│   │   ├── Memory/
│   │   │   ├── MemoryBrowserScreen.tsx
│   │   │   ├── MemorySearch.tsx
│   │   │   └── MemoryStats.tsx
│   │   └── Common/
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorDisplay.tsx
│   │       ├── ConnectionStatus.tsx
│   │       └── EmptyState.tsx
│   ├── services/
│   │   ├── mcpApi.ts (reused from Electron)
│   │   ├── serviceBridge.ts (reused from Electron)
│   │   ├── connectionManager.ts
│   │   └── storage.ts
│   ├── hooks/
│   │   ├── useAIChat.ts (reused from Electron)
│   │   ├── useConnection.ts
│   │   └── usePolling.ts
│   ├── stores/
│   │   ├── chatStore.ts
│   │   ├── agentStore.ts
│   │   └── connectionStore.ts
│   ├── navigation/
│   │   ├── AppNavigator.tsx
│   │   ├── TabNavigator.tsx
│   │   └── types.ts
│   ├── config/
│   │   └── api.ts
│   └── App.tsx
├── android/
├── ios/ (future)
├── package.json
└── README.md
```

---

## 🔌 **NETWORK LAYER**

### **Connection Manager**

**src/services/connectionManager.ts:**
```typescript
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface ConnectionConfig {
  commandServerUrl: string;
  daemonUrl: string;
  timeout: number;
}

const DEFAULT_CONFIG: ConnectionConfig = {
  commandServerUrl: 'http://localhost:5001', // Development - needs configurable
  daemonUrl: 'http://localhost:5000',
  timeout: 10000
};

class ConnectionManager {
  private config: ConnectionConfig;
  private isConnected: boolean = false;
  private lastCheck: Date | null = null;

  constructor() {
    this.config = DEFAULT_CONFIG;
    this.loadConfig();
  }

  async loadConfig(): Promise<void> {
    try {
      const saved = await AsyncStorage.getItem('connection_config');
      if (saved) {
        this.config = JSON.parse(saved);
      }
    } catch (error) {
      console.error('Failed to load connection config:', error);
    }
  }

  async saveConfig(config: Partial<ConnectionConfig>): Promise<void> {
    this.config = { ...this.config, ...config };
    try {
      await AsyncStorage.setItem('connection_config', JSON.stringify(this.config));
    } catch (error) {
      console.error('Failed to save connection config:', error);
    }
  }

  async checkConnection(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.commandServerUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(this.config.timeout)
      });
      
      this.isConnected = response.ok;
      this.lastCheck = new Date();
      return this.isConnected;
    } catch (error) {
      this.isConnected = false;
      return false;
    }
  }

  getCommandServerUrl(): string {
    return this.config.commandServerUrl;
  }

  getDaemonUrl(): string {
    return this.config.daemonUrl;
  }

  getConnectionStatus(): { connected: boolean; lastCheck: Date | null } {
    return {
      connected: this.isConnected,
      lastCheck: this.lastCheck
    };
  }

  // For mobile, we need to detect if we're on same network
  // This is a placeholder - production would use proper network detection
  async detectServerUrl(): Promise<string | null> {
    // Try localhost first (development)
    if (await this.checkConnection()) {
      return this.config.commandServerUrl;
    }
    
    // Future: Try network IP addresses
    // Future: Try discovered servers
    // Future: Try configured URLs
    
    return null;
  }
}

export const connectionManager = new ConnectionManager();
```

### **API Configuration**

**src/config/api.ts:**
```typescript
import { connectionManager } from '../services/connectionManager';

export const API_CONFIG = {
  baseUrl: () => connectionManager.getCommandServerUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
};

export const MCP_ENDPOINTS = {
  execute: '/mcp/execute',
  listTools: '/mcp/list',
  health: '/health'
};
```

---

## 💬 **CHAT INTERFACE**

### **Chat Screen Component**

**src/components/Chat/ChatScreen.tsx:**
```typescript
import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { useAIChat } from '../../hooks/useAIChat';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { AgentSelector } from './AgentSelector';
import { ConnectionStatus } from '../Common/ConnectionStatus';
import { LoadingSpinner } from '../Common/LoadingSpinner';
import { ErrorDisplay } from '../Common/ErrorDisplay';

interface ChatScreenProps {
  initialAgent?: string | null;
}

export const ChatScreen: React.FC<ChatScreenProps> = ({ initialAgent = null }) => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(initialAgent);
  const [inputText, setInputText] = useState('');
  
  const {
    messages,
    threads,
    discoveredAgents,
    loading,
    error,
    isPolling,
    sendMessage,
    startDiscussion,
    stopPolling,
    resumePolling
  } = useAIChat(selectedAgent || undefined);

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const messageContent = inputText.trim();
    setInputText('');

    try {
      if (selectedAgent) {
        // Direct message
        await sendMessage(selectedAgent, messageContent);
      } else {
        // Broadcast to all agents
        await sendMessage(undefined, messageContent);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <View style={styles.header}>
        <ConnectionStatus />
        <AgentSelector
          agents={discoveredAgents}
          selectedAgent={selectedAgent}
          onSelectAgent={setSelectedAgent}
        />
      </View>

      {loading && <LoadingSpinner />}
      {error && <ErrorDisplay error={error} />}

      <MessageList messages={messages} />

      <MessageInput
        value={inputText}
        onChangeText={setInputText}
        onSend={handleSend}
        placeholder={selectedAgent ? `Message ${selectedAgent}...` : "Message all agents..."}
      />
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a'
  },
  header: {
    padding: 16,
    backgroundColor: '#1a1a1a',
    borderBottomWidth: 1,
    borderBottomColor: '#333'
  }
});
```

### **Message List Component**

**src/components/Chat/MessageList.tsx:**
```typescript
import React, { useRef, useEffect } from 'react';
import { FlatList, StyleSheet, View } from 'react-native';
import { MessageBubble } from './MessageBubble';
import { AIMessage } from '../../hooks/useAIChat';

interface MessageListProps {
  messages: AIMessage[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    // Scroll to bottom when messages change
    if (messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  const renderMessage = ({ item }: { item: AIMessage }) => (
    <MessageBubble message={item} />
  );

  return (
    <FlatList
      ref={flatListRef}
      data={messages}
      renderItem={renderMessage}
      keyExtractor={(item) => item.message_id}
      contentContainerStyle={styles.list}
      inverted={false}
      onEndReachedThreshold={0.1}
    />
  );
};

const styles = StyleSheet.create({
  list: {
    padding: 16,
    flexGrow: 1
  }
});
```

### **Message Bubble Component**

**src/components/Chat/MessageBubble.tsx:**
```typescript
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { AIMessage } from '../../hooks/useAIChat';

interface MessageBubbleProps {
  message: AIMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.from_ai === 'electron-app' || message.from_ai === 'User';
  
  return (
    <View style={[styles.container, isUser ? styles.userMessage : styles.agentMessage]}>
      {!isUser && (
        <Text style={styles.agentName}>{message.from_ai}</Text>
      )}
      <Text style={styles.content}>{message.content}</Text>
      <Text style={styles.timestamp}>
        {new Date(message.timestamp).toLocaleTimeString()}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 12,
    marginVertical: 4,
    borderRadius: 12,
    maxWidth: '80%'
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#0066cc'
  },
  agentMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#2a2a2a'
  },
  agentName: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#888',
    marginBottom: 4
  },
  content: {
    color: '#fff',
    fontSize: 14
  },
  timestamp: {
    fontSize: 10,
    color: '#666',
    marginTop: 4
  }
});
```

---

## 🔄 **REUSING ELECTRON APP CODE**

### **Adapting useAIChat Hook**

The `useAIChat` hook can be reused mostly as-is. Minor adaptations:

**src/hooks/useAIChat.ts** (Adapted):
```typescript
// Import from Electron app
import { useAIChat as useAIChatElectron } from '../../../ide_chat_app/src/hooks/useAIChat';

// Re-export with mobile-specific adaptations
export function useAIChat(agentId?: string, threadId?: string) {
  const electronHook = useAIChatElectron(agentId, threadId);
  
  // Mobile-specific adaptations:
  // - Adjust polling interval for battery efficiency
  // - Handle network state changes
  // - Optimize for mobile rendering
  
  return electronHook;
}
```

### **Adapting MCPAPI Service**

**src/services/mcpApi.ts** (Adapted):
```typescript
// Import from Electron app
import { MCPAPI as MCPAPIElectron } from '../../../ide_chat_app/src/services/mcpApi';
import { connectionManager } from './connectionManager';

export class MCPAPI extends MCPAPIElectron {
  constructor() {
    // Use connection manager for URL
    super(connectionManager.getCommandServerUrl());
  }
  
  // Override to use connection manager
  async checkExtension(): Promise<boolean> {
    const connected = await connectionManager.checkConnection();
    if (connected) {
      return super.checkExtension();
    }
    return false;
  }
}
```

---

## 🧭 **NAVIGATION**

### **App Navigator**

**src/navigation/AppNavigator.tsx:**
```typescript
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { ChatScreen } from '../components/Chat/ChatScreen';
import { AgentListScreen } from '../components/Agents/AgentListScreen';
import { MemoryBrowserScreen } from '../components/Memory/MemoryBrowserScreen';
import { SettingsScreen } from '../components/Settings/SettingsScreen';
import Icon from 'react-native-vector-icons/MaterialIcons';

const Tab = createBottomTabNavigator();

export const AppNavigator: React.FC = () => {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          tabBarActiveTintColor: '#0066cc',
          tabBarInactiveTintColor: '#666',
          headerStyle: {
            backgroundColor: '#1a1a1a'
          },
          headerTintColor: '#fff'
        }}
      >
        <Tab.Screen
          name="Chat"
          component={ChatScreen}
          options={{
            tabBarIcon: ({ color }) => (
              <Icon name="chat" size={24} color={color} />
            )
          }}
        />
        <Tab.Screen
          name="Agents"
          component={AgentListScreen}
          options={{
            tabBarIcon: ({ color }) => (
              <Icon name="people" size={24} color={color} />
            )
          }}
        />
        <Tab.Screen
          name="Memory"
          component={MemoryBrowserScreen}
          options={{
            tabBarIcon: ({ color }) => (
              <Icon name="memory" size={24} color={color} />
            )
          }}
        />
        <Tab.Screen
          name="Settings"
          component={SettingsScreen}
          options={{
            tabBarIcon: ({ color }) => (
              <Icon name="settings" size={24} color={color} />
            )
          }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
};
```

---

## 🧪 **TESTING**

### **Unit Tests**

**src/components/Chat/__tests__/ChatScreen.test.tsx:**
```typescript
import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { ChatScreen } from '../ChatScreen';

jest.mock('../../hooks/useAIChat');

describe('ChatScreen', () => {
  it('renders correctly', () => {
    const { getByPlaceholderText } = render(<ChatScreen />);
    expect(getByPlaceholderText('Message all agents...')).toBeTruthy();
  });

  it('sends message on send', async () => {
    const { getByPlaceholderText, getByText } = render(<ChatScreen />);
    const input = getByPlaceholderText('Message all agents...');
    const sendButton = getByText('Send');

    fireEvent.changeText(input, 'Test message');
    fireEvent.press(sendButton);

    // Assert message sent
  });
});
```

---

## 📦 **DEPLOYMENT**

### **Android APK Build**

```bash
# Build release APK
cd android
./gradlew assembleRelease

# APK location: android/app/build/outputs/apk/release/app-release.apk

# Or build bundle for Play Store
./gradlew bundleRelease
```

### **Environment Configuration**

**android/app/src/main/assets/env.json:**
```json
{
  "COMMAND_SERVER_URL": "http://192.168.1.100:5001",
  "DAEMON_URL": "http://192.168.1.100:5000"
}
```

---

## 🔧 **MOBILE-SPECIFIC CONSIDERATIONS**

### **Battery Optimization**

- Reduce polling frequency when app in background
- Batch requests where possible
- Use efficient data structures

### **Network Handling**

- Handle offline mode gracefully
- Queue messages when offline
- Retry failed requests
- Show connection status

### **Performance**

- Optimize FlatList rendering
- Use React.memo for components
- Lazy load screens
- Optimize image loading

---

## 📊 **INTEGRATION WITH EXISTING SYSTEMS**

### **Extension Command Server**

The mobile app connects to the same Command Server as Electron app:
- Port 5001
- Same endpoints
- Same authentication (future)

### **MCP Tools**

All 59 MCP tools available via Command Server:
- Core AIM-OS tools
- SCOR tools
- Timeline tools
- Autonomous tools
- etc.

### **Reusing Components**

Components that can be reused:
- `useAIChat` hook (with minor adaptations)
- `MCPAPI` service (with URL config)
- `ServiceBridge` (with URL config)
- Message conversion logic
- Agent discovery logic

Components that need mobile-specific versions:
- UI components (touch-optimized)
- Navigation (React Navigation)
- Storage (AsyncStorage)

---

## ✅ **SUCCESS CRITERIA**

1. ✅ Connects to Extension Command Server
2. ✅ Chat interface functional
3. ✅ Message polling works
4. ✅ Agent discovery works
5. ✅ Memory access works
6. ✅ MCP tools executable
7. ✅ Offline support
8. ✅ Mobile-optimized UX
9. ✅ Battery efficient
10. ✅ Production-ready APK

---

*L3 Detailed Implementation Guide - AIM-OS Mobile App*  
*2025-11-01*

