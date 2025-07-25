/**
 * Color Palette Definitions
 * Semantic color mappings for Turkish Financial PDF RAG System
 */

// Base color palette
export const colors = {
  // Turkish flag inspired colors
  turkish: {
    red: {
      50: "hsl(0, 84%, 97%)",
      100: "hsl(0, 84%, 94%)",
      200: "hsl(0, 84%, 86%)",
      300: "hsl(0, 84%, 77%)",
      400: "hsl(0, 84%, 66%)",
      500: "hsl(0, 84%, 50%)",    // Primary red
      600: "hsl(0, 84%, 45%)",
      700: "hsl(0, 84%, 40%)",
      800: "hsl(0, 84%, 35%)",
      900: "hsl(0, 84%, 25%)",
      950: "hsl(0, 84%, 15%)",
    },
  },

  // Neutral grays
  gray: {
    50: "hsl(0, 0%, 98%)",
    100: "hsl(0, 0%, 95%)",
    200: "hsl(0, 0%, 90%)",
    300: "hsl(0, 0%, 85%)",
    400: "hsl(0, 0%, 70%)",
    500: "hsl(0, 0%, 50%)",
    600: "hsl(0, 0%, 40%)",
    700: "hsl(0, 0%, 30%)",
    800: "hsl(0, 0%, 20%)",
    900: "hsl(0, 0%, 10%)",
    950: "hsl(0, 0%, 5%)",
  },

  // Financial domain colors
  financial: {
    profit: {
      50: "hsl(142, 76%, 97%)",
      100: "hsl(142, 76%, 94%)",
      500: "hsl(142, 76%, 36%)",    // Success green
      600: "hsl(142, 76%, 31%)",
      700: "hsl(142, 76%, 26%)",
    },
    loss: {
      50: "hsl(0, 84%, 97%)",
      100: "hsl(0, 84%, 94%)",
      500: "hsl(0, 84%, 50%)",      // Loss red
      600: "hsl(0, 84%, 45%)",
      700: "hsl(0, 84%, 40%)",
    },
    neutral: {
      50: "hsl(38, 92%, 97%)",
      100: "hsl(38, 92%, 94%)",
      500: "hsl(38, 92%, 50%)",     // Warning orange
      600: "hsl(38, 92%, 45%)",
      700: "hsl(38, 92%, 40%)",
    },
    info: {
      50: "hsl(221, 83%, 97%)",
      100: "hsl(221, 83%, 94%)",
      500: "hsl(221, 83%, 53%)",    // Info blue
      600: "hsl(221, 83%, 48%)",
      700: "hsl(221, 83%, 43%)",
    },
  },

  // Chart and visualization colors
  chart: {
    primary: "hsl(0, 84%, 50%)",     // Turkish red
    secondary: "hsl(221, 83%, 53%)", // Blue
    tertiary: "hsl(142, 76%, 36%)",  // Green
    quaternary: "hsl(38, 92%, 50%)", // Orange
    quinary: "hsl(271, 91%, 65%)",   // Purple
    senary: "hsl(173, 58%, 39%)",    // Teal
  },

  // Status indicators
  status: {
    success: "hsl(142, 76%, 36%)",
    warning: "hsl(38, 92%, 50%)",
    error: "hsl(0, 84%, 50%)",
    info: "hsl(221, 83%, 53%)",
    processing: "hsl(38, 92%, 50%)",
    completed: "hsl(142, 76%, 36%)",
    failed: "hsl(0, 84%, 50%)",
  },
} as const;

// Semantic color mappings
export const semanticColors = {
  // Text colors
  text: {
    primary: colors.gray[950],
    secondary: colors.gray[700],
    muted: colors.gray[500],
    disabled: colors.gray[400],
    inverse: colors.gray[50],
  },

  // Background colors
  background: {
    primary: colors.gray[50],
    secondary: colors.gray[100],
    muted: colors.gray[200],
    inverse: colors.gray[950],
    overlay: "hsla(0, 0%, 0%, 0.5)",
  },

  // Border colors
  border: {
    default: colors.gray[200],
    muted: colors.gray[100],
    focus: colors.turkish.red[500],
    error: colors.financial.loss[500],
    success: colors.financial.profit[500],
  },

  // Interactive element colors
  interactive: {
    primary: colors.turkish.red[500],
    primaryHover: colors.turkish.red[600],
    primaryActive: colors.turkish.red[700],
    secondary: colors.gray[100],
    secondaryHover: colors.gray[200],
    secondaryActive: colors.gray[300],
  },

  // Financial data visualization
  financial: {
    positive: colors.financial.profit[500],
    negative: colors.financial.loss[500],
    neutral: colors.financial.neutral[500],
    volume: colors.gray[400],
    price: colors.turkish.red[500],
    index: colors.financial.info[500],
  },
} as const;

// Dark mode color overrides
export const darkColors = {
  text: {
    primary: colors.gray[50],
    secondary: colors.gray[300],
    muted: colors.gray[500],
    disabled: colors.gray[600],
    inverse: colors.gray[950],
  },

  background: {
    primary: colors.gray[950],
    secondary: colors.gray[900],
    muted: colors.gray[800],
    inverse: colors.gray[50],
    overlay: "hsla(0, 0%, 0%, 0.7)",
  },

  border: {
    default: colors.gray[800],
    muted: colors.gray[900],
    focus: colors.turkish.red[400],
    error: colors.financial.loss[400],
    success: colors.financial.profit[400],
  },

  interactive: {
    primary: colors.turkish.red[500],
    primaryHover: colors.turkish.red[400],
    primaryActive: colors.turkish.red[300],
    secondary: colors.gray[800],
    secondaryHover: colors.gray[700],
    secondaryActive: colors.gray[600],
  },
} as const;

// Utility function to get appropriate colors based on theme
export const getSemanticColors = (isDark: boolean = false) => {
  return isDark 
    ? { ...semanticColors, ...darkColors }
    : semanticColors;
};

// Color utility functions
export const withOpacity = (color: string, opacity: number): string => {
  // Convert HSL to HSLA with opacity
  if (color.startsWith('hsl(')) {
    return color.replace('hsl(', 'hsla(').replace(')', `, ${opacity})`);
  }
  return color;
};

export const lighten = (color: string, amount: number): string => {
  // Simple lightening by increasing the lightness value
  if (color.startsWith('hsl(')) {
    const match = color.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
    if (match) {
      const [, h, s, l] = match;
      const newL = Math.min(100, parseInt(l) + amount);
      return `hsl(${h}, ${s}%, ${newL}%)`;
    }
  }
  return color;
};

export const darken = (color: string, amount: number): string => {
  // Simple darkening by decreasing the lightness value
  if (color.startsWith('hsl(')) {
    const match = color.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
    if (match) {
      const [, h, s, l] = match;
      const newL = Math.max(0, parseInt(l) - amount);
      return `hsl(${h}, ${s}%, ${newL}%)`;
    }
  }
  return color;
};
