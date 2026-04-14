import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.firestation.mobile',
  appName: 'Fire Station Mobile',
  webDir: 'dist',
  
  // Пути к иконкам
  icon: 'src/assets/icons/icon.png',
  
  // Сплэш экран
  splash: {
    image: 'src/assets/icons/icon-512.png',
    backgroundColor: '#ffffff',
    showSpinner: false,
  },
  
  server: {
    androidScheme: 'http',
    cleartext: true,
    allowNavigation: ['192.168.1.199', 'localhost', '127.0.0.1'],
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 3000,
      launchAutoHide: true,
      backgroundColor: '#ffffff',
      showSpinner: false,
    },
    ScreenOrientation: {
      orientations: ['portrait'],
    },
    Capacitor: {
      handleURLOpen: true,
    },
  },
};

export default config;
