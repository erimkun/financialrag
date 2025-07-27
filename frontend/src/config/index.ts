/**
 * Environment Configuration
 * Centralized configuration management for the frontend application
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  ENDPOINTS: {
    UPLOAD: import.meta.env.VITE_API_UPLOAD_ENDPOINT || '/api/upload',
    QUERY: import.meta.env.VITE_API_QUERY_ENDPOINT || '/api/query', 
    DOCUMENTS: import.meta.env.VITE_API_DOCUMENTS_ENDPOINT || '/api/documents',
    HEALTH: import.meta.env.VITE_API_HEALTH_ENDPOINT || '/api/health',
  },
  TIMEOUT: parseInt(import.meta.env.VITE_REQUEST_TIMEOUT || '30000'),
  RETRY_ATTEMPTS: parseInt(import.meta.env.VITE_RETRY_ATTEMPTS || '3'),
} as const;

// Application Configuration
export const APP_CONFIG = {
  TITLE: import.meta.env.VITE_APP_TITLE || 'Turkish Financial AI Assistant',
  DESCRIPTION: import.meta.env.VITE_APP_DESCRIPTION || 'AI destekli finansal doküman analizi',
  VERSION: '2.0.0',
} as const;

// Theme Configuration
export const THEME_CONFIG = {
  DEFAULT_THEME: import.meta.env.VITE_DEFAULT_THEME || 'light',
  ENABLE_DARK_MODE: import.meta.env.VITE_ENABLE_DARK_MODE === 'true',
} as const;

// Feature Flags
export const FEATURE_FLAGS = {
  ENABLE_DEBUG: import.meta.env.VITE_ENABLE_DEBUG === 'true',
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  ENABLE_EXPERIMENTAL: import.meta.env.VITE_ENABLE_EXPERIMENTAL === 'true',
} as const;

// File Upload Configuration
export const UPLOAD_CONFIG = {
  MAX_FILE_SIZE_MB: parseInt(import.meta.env.VITE_MAX_FILE_SIZE_MB || '50'),
  MAX_FILE_SIZE_BYTES: parseInt(import.meta.env.VITE_MAX_FILE_SIZE_MB || '50') * 1024 * 1024,
  ALLOWED_FILE_TYPES: import.meta.env.VITE_ALLOWED_FILE_TYPES?.split(',') || ['.pdf'],
  CHUNK_SIZE: parseInt(import.meta.env.VITE_UPLOAD_CHUNK_SIZE || '1048576'),
} as const;

// Performance Configuration
export const PERFORMANCE_CONFIG = {
  SEARCH_DEBOUNCE: parseInt(import.meta.env.VITE_SEARCH_DEBOUNCE || '500'),
} as const;

// Development Configuration
export const DEV_CONFIG = {
  IS_DEVELOPMENT: import.meta.env.DEV,
  IS_PRODUCTION: import.meta.env.PROD,
  PORT: parseInt(import.meta.env.VITE_PORT || '5173'),
  HOST: import.meta.env.VITE_HOST || 'localhost',
} as const;

// Utility function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Utility function to check if feature is enabled
export const isFeatureEnabled = (feature: keyof typeof FEATURE_FLAGS): boolean => {
  return FEATURE_FLAGS[feature];
};

// Environment validation
export const validateEnvironment = (): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];
  
  // Check required environment variables
  if (!API_CONFIG.BASE_URL) {
    errors.push('VITE_API_BASE_URL is required');
  }
  
  // Validate API URL format
  try {
    new URL(API_CONFIG.BASE_URL);
  } catch {
    errors.push('VITE_API_BASE_URL must be a valid URL');
  }
  
  // Validate numeric values
  if (isNaN(API_CONFIG.TIMEOUT) || API_CONFIG.TIMEOUT <= 0) {
    errors.push('VITE_REQUEST_TIMEOUT must be a positive number');
  }
  
  if (isNaN(UPLOAD_CONFIG.MAX_FILE_SIZE_MB) || UPLOAD_CONFIG.MAX_FILE_SIZE_MB <= 0) {
    errors.push('VITE_MAX_FILE_SIZE_MB must be a positive number');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

// Export all configuration for easy access
export const config = {
  api: API_CONFIG,
  app: APP_CONFIG,
  theme: THEME_CONFIG,
  features: FEATURE_FLAGS,
  upload: UPLOAD_CONFIG,
  performance: PERFORMANCE_CONFIG,
  dev: DEV_CONFIG,
  getApiUrl,
  isFeatureEnabled,
  validateEnvironment,
} as const;

export default config;
