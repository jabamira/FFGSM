import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.firestation.mobile',
  appName: 'Fire Station Mobile',
  webDir: 'dist',
  server: {
    androidScheme: 'http',
    cleartext: true,
    allowNavigation: ['192.168.1.199', 'localhost', '127.0.0.1'],
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 0,
    },
    Capacitor: {
      handleURLOpen: true,
    },
  },
};

export default config;
