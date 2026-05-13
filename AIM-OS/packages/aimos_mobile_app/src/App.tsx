/**
 * AIM-OS Mobile App
 * Entry point for React Native application
 */

import React from 'react';
import { StatusBar } from 'react-native';
import { AppNavigator } from './src/navigation/AppNavigator';

const App: React.FC = () => {
  return (
    <>
      <StatusBar barStyle="light-content" backgroundColor="#0a0a0a" />
      <AppNavigator />
    </>
  );
};

export default App;

