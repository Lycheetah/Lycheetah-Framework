import AsyncStorage from '@react-native-async-storage/async-storage';
import type { TruthPressureKeyValueStore } from './shadow-store-core.ts';
import { createShadowRecorder } from './shadow-store-core.ts';

/**
 * Thin React Native adapter. The storage core remains platform-independent and
 * executable under tests with an in-memory store.
 */
export const truthPressureAsyncStorage: TruthPressureKeyValueStore = {
  getItem: key => AsyncStorage.getItem(key),
  setItem: (key, value) => AsyncStorage.setItem(key, value),
  removeItem: key => AsyncStorage.removeItem(key),
};

export const truthPressureShadowRecorder = createShadowRecorder(
  truthPressureAsyncStorage,
);
