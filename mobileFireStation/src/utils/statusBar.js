import { StatusBar, Style } from '@capacitor/status-bar'
import { Capacitor } from '@capacitor/core'

/**
 * Инициализирует цвет статус-бара (верхняя и нижняя система панель на Android)
 * Должна быть вызвана при загрузке приложения
 */
export const initStatusBar = async () => {
  if (!Capacitor.isNativePlatform()) {
    return
  }

  try {
    // StatusBar и NavigationBar конфигурируются в capacitor.config.ts
    // overlaysWebView: true делает их прозрачными

    console.log('[StatusBar] Initialized successfully - Transparent via capacitor.config.ts')
    console.log('[StatusBar] Note: Bars overlay content')
  } catch (error) {
    console.error('[StatusBar] Error initializing:', error)
  }
}

/**
 * Изменить цвет статус-бара
 * @param {string} color - HEX цвет (например '#ffffff')
 */
export const setStatusBarColor = async (color) => {
  if (!Capacitor.isNativePlatform()) {
    return
  }

  try {
    await StatusBar.setBackgroundColor({ color })
    console.log('[StatusBar] Color changed to:', color)
  } catch (error) {
    console.error('[StatusBar] Error setting color:', error)
  }
}

/**
 * Установить стиль статус-бара
 * @param {Style} style - Style.Light или Style.Dark
 */
export const setStatusBarStyle = async (style) => {
  if (!Capacitor.isNativePlatform()) {
    return
  }

  try {
    await StatusBar.setStyle({ style })
    console.log('[StatusBar] Style changed to:', style)
  } catch (error) {
    console.error('[StatusBar] Error setting style:', error)
  }
}
