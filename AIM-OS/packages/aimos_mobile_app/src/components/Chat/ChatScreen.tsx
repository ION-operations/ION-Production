/**
 * Chat Screen Component
 * Primary screen for mobile app - chat interface with agents
 */

import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform, ScrollView, TouchableOpacity, Text } from 'react-native';
import { useAIChat } from '../hooks/useAIChat';
import { MessageList } from './Chat/MessageList';
import { MessageInput } from './Chat/MessageInput';
import { AgentSelector } from './Chat/AgentSelector';
import { ConnectionStatus } from './Common/ConnectionStatus';
import { LoadingSpinner } from './Common/LoadingSpinner';
import { ErrorDisplay } from './Common/ErrorDisplay';

interface ChatScreenProps {
  initialAgent?: string | null;
}

export const ChatScreen: React.FC<ChatScreenProps> = ({ initialAgent = null }) => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(initialAgent);
  const [inputText, setInputText] = useState('');
  
  const {
    messages,
    discoveredAgents,
    loading,
    error,
    sendMessage,
    sendProceedCommand
  } = useAIChat(selectedAgent || undefined);

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const messageContent = inputText.trim();
    setInputText('');

    try {
      await sendMessage(selectedAgent || undefined, messageContent);
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  const handleProceed = async () => {
    try {
      await sendProceedCommand(selectedAgent || undefined, inputText.trim() || undefined);
      setInputText('');
    } catch (err) {
      console.error('Failed to send proceed command:', err);
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

      <View style={styles.inputContainer}>
        <MessageInput
          value={inputText}
          onChangeText={setInputText}
          onSend={handleSend}
          placeholder={selectedAgent ? `Message ${selectedAgent}...` : "Message all agents or type 'proceed'..."}
        />
        <TouchableOpacity 
          style={styles.proceedButton}
          onPress={handleProceed}
        >
          <Text style={styles.proceedButtonText}>Proceed</Text>
        </TouchableOpacity>
      </View>
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
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#1a1a1a',
    borderTopWidth: 1,
    borderTopColor: '#333',
    alignItems: 'center'
  },
  proceedButton: {
    backgroundColor: '#0066cc',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 8,
    marginLeft: 8
  },
  proceedButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14
  }
});

