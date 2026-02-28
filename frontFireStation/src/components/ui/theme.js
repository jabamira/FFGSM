/**
 * Centralized theme configuration for custom components
 * Easily customize colors, sizes, and spacing here
 */

// Brand color palette
export const palette = {
  dark: "#405267",
  medium: "#7C91A6",
  primary: "#4A99B2",
  secondary: "#4486A5",
  light: "#AFB1B4",
  white: "#FFFFFF",
  error: "#E74C3C",
  success: "#27AE60",
  warning: "#F39C12",
};

export const theme = {
  colors: {
    primary: palette.primary,
    secondary: palette.secondary,
    dark: palette.dark,
    medium: palette.medium,
    light: palette.light,
    danger: palette.error,
    success: palette.success,
    warning: palette.warning,
  },

  button: {
    sizes: {
      xs: "px-2 py-1 text-xs",
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-base",
      lg: "px-6 py-3 text-lg",
      xl: "px-8 py-4 text-xl",
    },
  },

  input: {
    sizes: {
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-base",
      lg: "px-5 py-3 text-lg",
    },
  },

  table: {
    sizes: {
      sm: "text-xs",
      md: "text-sm",
      lg: "text-base",
    },
  },

  modal: {
    overlay:
      "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center",
    content:
      "bg-white rounded-lg shadow-lg max-w-lg w-full max-h-96 overflow-y-auto",
  },
};

/**
 * Helper function to get color from palette
 */
export const getColor = (colorKey) => {
  return palette[colorKey] || palette.primary;
};

/**
 * Helper function to build class strings with variants
 */
export const buildClass = (baseClass, variants = {}) => {
  return (
    Object.entries(variants)
      .filter(([, value]) => value)
      .map(([key]) => key)
      .join(" ") || baseClass
  );
};
