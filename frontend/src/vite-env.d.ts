/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_API_UPLOAD_ENDPOINT: string
  readonly VITE_API_QUERY_ENDPOINT: string
  readonly VITE_API_DOCUMENTS_ENDPOINT: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
