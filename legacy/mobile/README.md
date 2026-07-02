# EIP Mobile App (React Native)

## Overview
Mobile application for the Entrepreneurship Intelligence Platform, built with React Native for iOS and Android.

## Features
- 🔐 Authentication (Login/Register)
- 💬 AI Chat Interface
- 📊 Dashboard with metrics
- 📄 Document upload and analysis
- 🔔 Push notifications
- 📱 Offline mode support

## Tech Stack
- React Native 0.72+
- TypeScript
- Redux Toolkit (State Management)
- React Navigation
- Axios (API calls)
- AsyncStorage (Local storage)
- React Native Paper (UI Components)

## Prerequisites
- Node.js 18+
- React Native CLI
- Xcode (for iOS)
- Android Studio (for Android)

## Setup

### Install Dependencies
```bash
cd mobile
npm install
# or
yarn install
```

### iOS Setup
```bash
cd ios
pod install
cd ..
```

### Run on iOS
```bash
npm run ios
# or
react-native run-ios
```

### Run on Android
```bash
npm run android
# or
react-native run-android
```

## Project Structure
```
mobile/
├── src/
│   ├── screens/          # Screen components
│   │   ├── Auth/         # Login, Register
│   │   ├── Dashboard/    # Main dashboard
│   │   ├── Chat/         # AI chat interface
│   │   └── Settings/     # User settings
│   ├── components/       # Reusable components
│   ├── navigation/       # Navigation configuration
│   ├── services/         # API services
│   ├── store/            # Redux store
│   ├── utils/            # Utility functions
│   └── types/            # TypeScript types
├── ios/                  # iOS native code
├── android/              # Android native code
├── package.json
└── tsconfig.json
```

## Environment Configuration

Create `.env` file:
```bash
API_BASE_URL=https://api.eip-platform.com
API_KEY=your-api-key
```

## Building for Production

### iOS
```bash
cd ios
pod install
cd ..
react-native run-ios --configuration Release
```

### Android
```bash
cd android
./gradlew assembleRelease
```

## Key Features Implementation

### 1. Authentication
- JWT token storage
- Automatic token refresh
- Biometric authentication support

### 2. AI Chat
- Real-time messaging
- Conversation history
- Agent identification
- Typing indicators

### 3. Dashboard
- Business metrics visualization
- Interactive charts (react-native-chart-kit)
- Pull-to-refresh

### 4. Document Upload
- Camera integration
- Gallery selection
- OCR preview
- Upload progress

### 5. Push Notifications
- Firebase Cloud Messaging
- Local notifications
- Notification settings

## API Integration

Base API service in `src/services/api.ts`:
```typescript
import axios from 'axios';

const API_BASE_URL = process.env.API_BASE_URL;

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## State Management

Redux store structure:
- `auth`: User authentication state
- `chat`: Chat messages and sessions
- `dashboard`: Business metrics
- `settings`: User preferences

## Testing

```bash
# Unit tests
npm test

# E2E tests (with Detox)
npm run e2e:ios
npm run e2e:android
```

## Deployment

### iOS App Store
1. Update version in `ios/EIP/Info.plist`
2. Build archive in Xcode
3. Upload to App Store Connect
4. Submit for review

### Google Play Store
1. Update version in `android/app/build.gradle`
2. Generate signed APK/AAB
3. Upload to Google Play Console
4. Submit for review

## Performance Optimization
- Code splitting
- Image optimization
- Lazy loading
- Memory leak prevention
- Bundle size optimization

## Security
- Secure storage for sensitive data
- Certificate pinning
- ProGuard (Android)
- Code obfuscation

## Contributing
See main project CONTRIBUTING.md

## License
Proprietary - All Rights Reserved

## Support
For support: mobile-support@eip-platform.com
