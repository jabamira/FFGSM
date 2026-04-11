import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.firestation.mobile',
  appName: 'Fire Station Mobile',
  webDir: 'dist',
  server: {
    androidScheme: 'https'
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
