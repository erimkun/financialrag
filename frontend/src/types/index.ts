// API Types
export interface QueryRequest {
  question: string;
  document_id?: string;
  language: string;
}

export interface QueryResponse {
  answer: string;
  confidence: number;
  response_time: number;
  document_id?: string;
  timestamp: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  size: number;
  pages: number;
  processed_at: string;
  status: string;
}

export interface SystemStats {
  total_documents: number;
  total_queries: number;
  avg_response_time: number;
  avg_confidence: number;
  system_status: string;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  rag_system: string;
  test_response_time: number;
  version: string;
}

export interface UploadResponse {
  document_id: string;
  filename: string;
  size: number;
  status: string;
  message: string;
}

// UI Types
export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  confidence?: number;
  responseTime?: number;
  isLoading?: boolean;
}

export interface UploadedDocument {
  id: string;
  filename: string;
  size: number;
  status: 'uploading' | 'completed' | 'error';
  message?: string;
}
