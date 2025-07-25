/**
 * Turkish Financial PDF RAG System - Theme Configuration
 * Centralized theme management with easy customization support
 */

export interface ThemeColors {
  primary: string;
  secondary: string;
  background: string;
  foreground: string;
  accent: string;
  muted: string;
  border: string;
  input: string;
  ring: string;
  success: string;
  warning: string;
  error: string;
  destructive: string;
}

export interface ThemeConfig {
  colors: ThemeColors;
  typography: {
    fontFamily: string;
    headingFont: string;
    fontSize: {
      xs: string;
      sm: string;
      base: string;
      lg: string;
      xl: string;
      '2xl': string;
      '3xl': string;
      '4xl': string;
    };
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
    '2xl': string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  animations: {
    duration: string;
    easing: string;
  };
}

// Default theme - Turkish Financial (Red, Black, White)
export const defaultTheme: ThemeConfig = {
  colors: {
    primary: "hsl(0, 84%, 50%)",        // Turkish red
    secondary: "hsl(0, 0%, 20%)",       // Dark gray
    background: "hsl(0, 0%, 98%)",      // Off-white
    foreground: "hsl(0, 0%, 5%)",       // Pure black
    accent: "hsl(0, 84%, 55%)",         // Lighter red
    muted: "hsl(0, 0%, 85%)",          // Light gray
    border: "hsl(0, 0%, 90%)",         // Border gray
    input: "hsl(0, 0%, 95%)",          // Input background
    ring: "hsl(0, 84%, 50%)",          // Focus ring
    success: "hsl(142, 76%, 36%)",     // Green
    warning: "hsl(38, 92%, 50%)",      // Orange
    error: "hsl(0, 84%, 60%)",         // Error red
    destructive: "hsl(0, 84%, 60%)",   // Destructive red
  },
  typography: {
    fontFamily: "Inter, system-ui, -apple-system, sans-serif",
    headingFont: "Poppins, Inter, system-ui, sans-serif",
    fontSize: {
      xs: "0.75rem",
      sm: "0.875rem",
      base: "1rem",
      lg: "1.125rem",
      xl: "1.25rem",
      '2xl': "1.5rem",
      '3xl': "1.875rem",
      '4xl': "2.25rem",
    },
  },
  spacing: {
    xs: "0.5rem",
    sm: "0.75rem",
    md: "1rem",
    lg: "1.5rem",
    xl: "2rem",
    '2xl': "3rem",
  },
  borderRadius: {
    sm: "0.25rem",
    md: "0.375rem",
    lg: "0.5rem",
    xl: "0.75rem",
  },
  animations: {
    duration: "200ms",
    easing: "cubic-bezier(0.4, 0, 0.2, 1)",
  },
};

// Alternative theme variants for easy switching
export const themeVariants = {
  // Blue variant for financial institutions
  blue: {
    ...defaultTheme,
    colors: {
      ...defaultTheme.colors,
      primary: "hsl(221, 83%, 53%)",     // Blue
      accent: "hsl(221, 83%, 58%)",      // Lighter blue
      ring: "hsl(221, 83%, 53%)",       // Blue focus ring
    },
  },
  
  // Green variant for growth/success themes
  green: {
    ...defaultTheme,
    colors: {
      ...defaultTheme.colors,
      primary: "hsl(142, 76%, 36%)",     // Green
      accent: "hsl(142, 76%, 41%)",      // Lighter green
      ring: "hsl(142, 76%, 36%)",       // Green focus ring
    },
  },
  
  // Dark mode variant
  dark: {
    ...defaultTheme,
    colors: {
      primary: "hsl(0, 84%, 50%)",       // Turkish red (same)
      secondary: "hsl(0, 0%, 80%)",      // Light gray
      background: "hsl(0, 0%, 8%)",      // Dark background
      foreground: "hsl(0, 0%, 95%)",     // Light text
      accent: "hsl(0, 84%, 55%)",        // Lighter red
      muted: "hsl(0, 0%, 25%)",          // Dark muted
      border: "hsl(0, 0%, 20%)",         // Dark border
      input: "hsl(0, 0%, 15%)",          // Dark input
      ring: "hsl(0, 84%, 50%)",          // Red focus ring
      success: "hsl(142, 76%, 41%)",     // Brighter green for dark
      warning: "hsl(38, 92%, 55%)",      // Brighter orange for dark
      error: "hsl(0, 84%, 65%)",         // Brighter red for dark
      destructive: "hsl(0, 84%, 65%)",   // Brighter destructive
    },
  },
  
  // High contrast variant for accessibility
  highContrast: {
    ...defaultTheme,
    colors: {
      primary: "hsl(0, 100%, 35%)",      // Darker red for contrast
      secondary: "hsl(0, 0%, 0%)",       // Pure black
      background: "hsl(0, 0%, 100%)",    // Pure white
      foreground: "hsl(0, 0%, 0%)",      // Pure black
      accent: "hsl(0, 100%, 40%)",       // Darker accent
      muted: "hsl(0, 0%, 60%)",          // Higher contrast muted
      border: "hsl(0, 0%, 50%)",         // Darker border
      input: "hsl(0, 0%, 100%)",         // White input
      ring: "hsl(0, 100%, 35%)",         // High contrast ring
      success: "hsl(142, 100%, 25%)",    // Darker green
      warning: "hsl(38, 100%, 35%)",     // Darker orange
      error: "hsl(0, 100%, 40%)",        // Darker error
      destructive: "hsl(0, 100%, 40%)",  // Darker destructive
    },
  },
};

// Theme utility functions
export const getTheme = (variant: keyof typeof themeVariants = 'blue'): ThemeConfig => {
  return themeVariants[variant] || defaultTheme;
};

export const generateCSSVariables = (theme: ThemeConfig): string => {
  return `
    :root {
      --color-primary: ${theme.colors.primary};
      --color-secondary: ${theme.colors.secondary};
      --color-background: ${theme.colors.background};
      --color-foreground: ${theme.colors.foreground};
      --color-accent: ${theme.colors.accent};
      --color-muted: ${theme.colors.muted};
      --color-border: ${theme.colors.border};
      --color-input: ${theme.colors.input};
      --color-ring: ${theme.colors.ring};
      --color-success: ${theme.colors.success};
      --color-warning: ${theme.colors.warning};
      --color-error: ${theme.colors.error};
      --color-destructive: ${theme.colors.destructive};
      
      --font-family: ${theme.typography.fontFamily};
      --font-heading: ${theme.typography.headingFont};
      
      --spacing-xs: ${theme.spacing.xs};
      --spacing-sm: ${theme.spacing.sm};
      --spacing-md: ${theme.spacing.md};
      --spacing-lg: ${theme.spacing.lg};
      --spacing-xl: ${theme.spacing.xl};
      --spacing-2xl: ${theme.spacing['2xl']};
      
      --radius-sm: ${theme.borderRadius.sm};
      --radius-md: ${theme.borderRadius.md};
      --radius-lg: ${theme.borderRadius.lg};
      --radius-xl: ${theme.borderRadius.xl};
      
      --animation-duration: ${theme.animations.duration};
      --animation-easing: ${theme.animations.easing};
    }
  `;
};

// Theme context type
export interface ThemeContextType {
  theme: ThemeConfig;
  setTheme: (variant: keyof typeof themeVariants) => void;
  currentVariant: keyof typeof themeVariants;
  isDark: boolean;
  toggleDark: () => void;
}

// Available theme options for UI
export const themeOptions = [
  { key: 'blue' as const, name: 'Klasik Mavi', description: 'Finansal kurumlar için mavi tema' },
  { key: 'green' as const, name: 'Büyüme Yeşili', description: 'Başarı ve büyüme teması' },
  { key: 'dark' as const, name: 'Karanlık Mod', description: 'Göz yorgunluğunu azaltan karanlık tema' },
  { key: 'highContrast' as const, name: 'Yüksek Kontrast', description: 'Erişilebilirlik için yüksek kontrast' },
] as const;
