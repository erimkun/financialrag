/**
 * Theme Context Provider
 * Provides theme management and easy customization throughout the app
 */

import React, { createContext, useContext, useEffect, useState } from 'react';
import { 
  ThemeConfig, 
  ThemeContextType, 
  defaultTheme, 
  themeVariants, 
  generateCSSVariables 
} from '../theme/config';

// Create the theme context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Theme provider component
interface ThemeProviderProps {
  children: React.ReactNode;
  defaultVariant?: keyof typeof themeVariants;
  storageKey?: string;
}

export function ThemeProvider({ 
  children, 
  defaultVariant = 'blue',
  storageKey = 'turkish-rag-theme'
}: ThemeProviderProps) {
  const [currentVariant, setCurrentVariant] = useState<keyof typeof themeVariants>(defaultVariant);
  const [isDark, setIsDark] = useState(false);
  const [theme, setTheme] = useState<ThemeConfig>(defaultTheme);

  // Load theme from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        const { variant, dark } = JSON.parse(stored);
        if (variant && variant in themeVariants) {
          setCurrentVariant(variant);
        }
        if (typeof dark === 'boolean') {
          setIsDark(dark);
        }
      }
    } catch (error) {
      console.warn('Failed to load theme from localStorage:', error);
    }
  }, [storageKey]);

  // Update theme when variant or dark mode changes
  useEffect(() => {
    const selectedTheme = themeVariants[currentVariant] || defaultTheme;
    
    // Apply dark mode overrides if enabled
    if (isDark && currentVariant !== 'dark') {
      const darkTheme = {
        ...selectedTheme,
        colors: {
          ...selectedTheme.colors,
          background: "hsl(0, 0%, 8%)",
          foreground: "hsl(0, 0%, 95%)",
          secondary: "hsl(0, 0%, 80%)",
          muted: "hsl(0, 0%, 25%)",
          border: "hsl(0, 0%, 20%)",
          input: "hsl(0, 0%, 15%)",
        },
      };
      setTheme(darkTheme);
    } else {
      setTheme(selectedTheme);
    }
  }, [currentVariant, isDark]);

  // Apply CSS variables to document
  useEffect(() => {
    const root = document.documentElement;
    const cssVariables = generateCSSVariables(theme);
    
    // Create a style element and inject CSS variables
    const styleElement = document.getElementById('theme-vars') || document.createElement('style');
    styleElement.id = 'theme-vars';
    styleElement.textContent = cssVariables;
    
    if (!document.getElementById('theme-vars')) {
      document.head.appendChild(styleElement);
    }

    // Apply dark class to html element for Tailwind
    if (isDark || currentVariant === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Save to localStorage
    try {
      localStorage.setItem(storageKey, JSON.stringify({
        variant: currentVariant,
        dark: isDark
      }));
    } catch (error) {
      console.warn('Failed to save theme to localStorage:', error);
    }
  }, [theme, isDark, currentVariant, storageKey]);

  // Theme switching functions
  const setThemeVariant = (variant: keyof typeof themeVariants) => {
    setCurrentVariant(variant);
    
    // Auto-enable dark mode for dark variant
    if (variant === 'dark') {
      setIsDark(true);
    } else if (currentVariant === 'dark') {
      setIsDark(false);
    }
  };

  const toggleDark = () => {
    setIsDark(!isDark);
  };

  const contextValue: ThemeContextType = {
    theme,
    setTheme: setThemeVariant,
    currentVariant,
    isDark: isDark || currentVariant === 'dark',
    toggleDark,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
}

// Custom hook to use theme context
export function useTheme() {
  const context = useContext(ThemeContext);
  
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  
  return context;
}

// Theme selector component for easy theme switching
interface ThemeSelectorProps {
  className?: string;
}

export function ThemeSelector({ className = "" }: ThemeSelectorProps) {
  const { currentVariant, setTheme, isDark, toggleDark } = useTheme();

  const themeOptions = [
    { key: 'blue' as const, name: 'Klasik Mavi', description: 'Finansal kurumlar için mavi tema' },
    { key: 'green' as const, name: 'Büyüme Yeşili', description: 'Başarı ve büyüme teması' },
    { key: 'dark' as const, name: 'Karanlık Mod', description: 'Göz yorgunluğunu azaltan karanlık tema' },
    { key: 'highContrast' as const, name: 'Yüksek Kontrast', description: 'Erişilebilirlik için yüksek kontrast' },
  ] as const;

  return (
    <div className={`space-y-4 ${className}`}>
      <div>
        <h3 className="text-sm font-medium mb-2">Tema Seçimi</h3>
        <div className="grid grid-cols-2 gap-2">
          {themeOptions.map((option) => (
            <button
              key={option.key}
              onClick={() => setTheme(option.key)}
              className={`
                p-3 rounded-lg border text-left transition-colors
                ${currentVariant === option.key 
                  ? 'border-primary bg-primary/10 text-primary' 
                  : 'border-border hover:bg-muted'
                }
              `}
            >
              <div className="font-medium text-sm">{option.name}</div>
              <div className="text-xs text-muted-foreground mt-1">
                {option.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {currentVariant !== 'dark' && (
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-medium">Karanlık Mod</div>
            <div className="text-xs text-muted-foreground">
              Göz yorgunluğunu azaltır
            </div>
          </div>
          <button
            onClick={toggleDark}
            className={`
              relative inline-flex h-6 w-11 items-center rounded-full transition-colors
              ${isDark ? 'bg-primary' : 'bg-muted'}
            `}
          >
            <span
              className={`
                inline-block h-4 w-4 transform rounded-full bg-background transition-transform
                ${isDark ? 'translate-x-6' : 'translate-x-1'}
              `}
            />
          </button>
        </div>
      )}
    </div>
  );
}

// Theme preview component
export function ThemePreview() {
  const { theme } = useTheme();

  return (
    <div className="p-4 space-y-4 border rounded-lg">
      <h4 className="font-medium">Tema Önizleme</h4>
      
      {/* Color palette */}
      <div className="grid grid-cols-4 gap-2">
        <div 
          className="h-8 rounded flex items-center justify-center text-xs font-medium"
          style={{ backgroundColor: theme.colors.primary, color: theme.colors.background }}
        >
          Ana Renk
        </div>
        <div 
          className="h-8 rounded flex items-center justify-center text-xs font-medium"
          style={{ backgroundColor: theme.colors.secondary, color: theme.colors.background }}
        >
          İkincil
        </div>
        <div 
          className="h-8 rounded flex items-center justify-center text-xs font-medium"
          style={{ backgroundColor: theme.colors.accent, color: theme.colors.background }}
        >
          Vurgu
        </div>
        <div 
          className="h-8 rounded flex items-center justify-center text-xs font-medium border"
          style={{ 
            backgroundColor: theme.colors.background, 
            color: theme.colors.foreground,
            borderColor: theme.colors.border
          }}
        >
          Arkaplan
        </div>
      </div>

      {/* Typography preview */}
      <div className="space-y-2">
        <h5 
          className="text-lg font-semibold"
          style={{ fontFamily: theme.typography.headingFont }}
        >
          Başlık Örneği
        </h5>
        <p style={{ fontFamily: theme.typography.fontFamily }}>
          Bu bir paragraf örneğidir. Türkçe finansal dökümanlar için optimize edilmiştir.
        </p>
      </div>
    </div>
  );
}
