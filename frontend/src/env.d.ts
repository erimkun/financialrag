/// <reference types="vite/client" />

interface ImportMetaEnv {
  // API Configuration
  readonly VITE_API_BASE_URL: string
  readonly VITE_API_UPLOAD_ENDPOINT: string
  readonly VITE_API_QUERY_ENDPOINT: string
  readonly VITE_API_DOCUMENTS_ENDPOINT: string
  readonly VITE_API_HEALTH_ENDPOINT: string
  
  // App Configuration
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_DESCRIPTION: string
  
  // Theme Configuration
  readonly VITE_DEFAULT_THEME: string
  readonly VITE_ENABLE_DARK_MODE: string
  
  // Feature Flags
  readonly VITE_ENABLE_DEBUG: string
  readonly VITE_ENABLE_ANALYTICS: string
  readonly VITE_ENABLE_EXPERIMENTAL: string
  
  // Upload Configuration
  readonly VITE_MAX_FILE_SIZE_MB: string
  readonly VITE_ALLOWED_FILE_TYPES: string
  readonly VITE_UPLOAD_CHUNK_SIZE: string
  
  // Performance Configuration
  readonly VITE_REQUEST_TIMEOUT: string
  readonly VITE_RETRY_ATTEMPTS: string
  readonly VITE_SEARCH_DEBOUNCE: string
  
  // Development Configuration
  readonly VITE_PORT: string
  readonly VITE_HOST: string
  readonly VITE_HMR: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
